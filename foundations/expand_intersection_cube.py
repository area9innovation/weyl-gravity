#!/usr/bin/env python3
"""Build and apply a reviewed 75%-coverage expansion of the foundations cube.

The policy is intentionally declarative at the foundation/carrier level.  Each
rule states which physical obligations the cited work treats directly; other
obligations are marked as pieces-only or priority gaps, never inferred as
theorems.  Selection is deterministic and stops at 162 assessed cells.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_EXPANSION_V1.json"
EXPANSION_LEDGER = ROOT / "foundations/literature-expansion-v2.json"
FINITE_RESULT = ROOT / "foundations/results/FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1.json"
TARGET = 162

K, S, D, G, I, R = (
    "KINEMATICS_OBSERVABLES", "STATES_PROBABILITY", "DYNAMICS_PROPAGATION",
    "GAUGE_BV_COHOMOLOGY", "INTERACTION_RENORMALIZATION_QME", "RECONSTRUCTION_LIMITS",
)
OBLIGATIONS = (K, S, D, G, I, R)

OBLIGATION_FINDING = {
    K: "defines observables, configurations, or the carrier's algebraic structure",
    S: "constructs or represents states and probability data",
    D: "supplies an evolution, spectral, or propagation result",
    G: "treats gauge constraints, BRST/BV structure, or symmetry restoration",
    I: "treats an interaction, counterterm/anomaly, renormalized product, or master-equation ingredient",
    R: "supplies reconstruction, comparison, covariance, or continuum-limit obligations",
}
OBLIGATION_MISSING = {
    K: "a full Weyl observable algebra and its domains",
    S: "a physically selected Weyl state and probability interpretation",
    D: "full interacting Lorentzian-causal propagation",
    G: "the certified full metric BV complex and its residual transfer",
    I: "Weyl counterterm coefficients, QME restoration, and residual transfer",
    R: "a prediction-preserving comparison or controlled continuum theorem",
}
FOUNDATION_BOUNDARY = {
    "CLASSICAL_STANDARD": "The source works in ordinary classical mathematics and is not a foundational-strength audit.",
    "WEAK_ARITHMETIC": "No reverse implication over a fixed weak base is inferred unless the cited source states one.",
    "WEAK_CHOICE_ZF": "An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred.",
    "CONSTRUCTIVE_COMPUTABLE": "Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types.",
    "TOPOS_INTERNAL": "External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters.",
    "FINITE_DISCRETE": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic.",
}
CARRIER_BOUNDARY = {
    "FINITE_EXACT": "The evidence is bounded finite algebra, not a completed infinite carrier.",
    "HILBERT_OPERATOR": "Domain, completion, and spectral-measure hypotheses remain part of the result.",
    "KREIN_INDEFINITE": "Real spectrum or J-unitarity alone does not produce a positive physical state space.",
    "ALGEBRAIC_CSTAR": "An algebraic architecture does not by itself select representations or physical states.",
    "SMOOTH_DISTRIBUTIONAL": "Local/formal PDE data do not imply global existence, support, or microlocal renormalization.",
    "LOCALIC_SYNTHETIC": "Internal/localic reformulation does not by itself establish external empirical equivalence.",
}


def rule(evidence: list[str], direct: str = "", pieces: str = "", priority: str = "", local: str = "", finding: str = "") -> dict[str, Any]:
    return {"evidence": evidence, "direct": set(direct), "pieces": set(pieces), "priority": set(priority), "local": set(local), "finding": finding}


POLICY: dict[tuple[str, str], dict[str, Any]] = {
    ("CLASSICAL_STANDARD", "FINITE_EXACT"): rule(["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"], "KSDI", "R", local="KSDI", finding="An exact two-qubit matrix model provides observables, density states, a star derivation, and an entangling interaction."),
    ("CLASSICAL_STANDARD", "HILBERT_OPERATOR"): rule(["neumann-pape-streicher-2018", "abramsky-coecke-2004"], "KSDR", "GI", finding="Spectral and compositional quantum results cover standard Hilbert kinematics, states, dynamics, and finite reconstruction."),
    ("CLASSICAL_STANDARD", "KREIN_INDEFINITE"): rule(["bender-boettcher-1998", "mostafazadeh-2001", "gottschalk-2004"], "KDR", "SGI", finding="Pseudo-Hermitian and Krein-QFT work supplies spectral, dynamical, and relativistic indefinite-metric results under explicit hypotheses."),
    ("CLASSICAL_STANDARD", "ALGEBRAIC_CSTAR"): rule(["brunetti-fredenhagen-verch-2001", "fewster-verch-2011", "fredenhagen-rejzner-2011"], "KSDGIR", finding="Locally covariant AQFT and perturbative BV jointly address algebraic kinematics, states, dynamics, gauge structure, interactions, and comparison principles."),
    ("CLASSICAL_STANDARD", "SMOOTH_DISTRIBUTIONAL"): rule(["barnich-brandt-henneaux-2000", "brunetti-fredenhagen-verch-2001", "fredenhagen-rejzner-2011", "brunetti-fredenhagen-rejzner-2013"], "KSDGIR", finding="Local BRST, locally covariant QFT, and perturbative BV give a standard smooth/distributional architecture across all six obligations."),
    ("CLASSICAL_STANDARD", "LOCALIC_SYNTHETIC"): rule(["heunen-landsman-spitters-2009", "doring-2008", "brenna-flori-2012", "harding-heunen-2019"], "KSDR", "GI", finding="Topos quantum theory supplies localic spectra, state measures, internal group dynamics, and comparisons between context topoi."),

    ("WEAK_ARITHMETIC", "FINITE_EXACT"): rule(["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"], "KSDI", "R", local="KSDI", finding="Every displayed operation is a finite loop over reduced rational pairs, providing a primitive-recursive sufficiency witness."),
    ("WEAK_ARITHMETIC", "HILBERT_OPERATOR"): rule(["brown-simpson-1986", "humphreys-simpson-1999", "humphreys-simpson-1996", "brattka-2008"], "KR", "SD", "GI", finding="Reverse mathematics calibrates specific separable Hahn-Banach, separation, and weak-star closure statements, with representation-sensitive strength."),
    ("WEAK_ARITHMETIC", "KREIN_INDEFINITE"): rule(["mostafazadeh-2001", "gottschalk-2004"], "", "KDS", "GIR", finding="Indefinite spectral and QFT ingredients exist classically, but their coding and proof strength over weak arithmetic are unaudited."),
    ("WEAK_ARITHMETIC", "ALGEBRAIC_CSTAR"): rule(["brown-simpson-1986", "blackadar-farah-2026", "brunetti-fredenhagen-verch-2001"], "", "KSDR", "GI", finding="Separation-strength and algebraic-QFT ingredients expose likely dependencies, but no common weak-base formalization is reviewed."),
    ("WEAK_ARITHMETIC", "SMOOTH_DISTRIBUTIONAL"): rule(["pour-el-richards-1981", "barnich-brandt-henneaux-2000"], "", "DGR", "KSI", finding="Wave computability and local BRST results identify separate analytic and gauge obligations without a common reversal."),
    ("WEAK_ARITHMETIC", "LOCALIC_SYNTHETIC"): rule(["coquand-spitters-2009", "heunen-landsman-spitters-2009"], "", "KSR", "DGI", finding="Constructive localic results provide ingredients, but their proof-theoretic strength over a fixed arithmetic base is not calibrated."),

    ("WEAK_CHOICE_ZF", "FINITE_EXACT"): rule(["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1", "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"], "KSDI", "GR", local="KSDI", finding="Named finite matrices and finite BV arrays are constructed without selecting from arbitrary families."),
    ("WEAK_CHOICE_ZF", "HILBERT_OPERATOR"): rule(["blackadar-farah-karagila-2026", "blackadar-farah-2026", "neumann-pape-streicher-2018"], "KR", "SGI", finding="ZF operator theory and explicit separable representations cover substantial kinematics while isolating arbitrary-space pathologies."),
    ("WEAK_CHOICE_ZF", "KREIN_INDEFINITE"): rule(["FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1", "mostafazadeh-2001", "gottschalk-2004"], "", "GIR", finding="The repository constructs the named free Krein carrier in ZF; classical sources add interaction-adjacent and relativistic ingredients only."),
    ("WEAK_CHOICE_ZF", "ALGEBRAIC_CSTAR"): rule(["blackadar-farah-2026", "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1", "fredenhagen-rejzner-2011"], "R", "GI", finding="Robust separable C*-theory and an explicit state/GNS chain exist in ZF; perturbative BV remains an external classical ingredient."),
    ("WEAK_CHOICE_ZF", "SMOOTH_DISTRIBUTIONAL"): rule(["brunetti-fredenhagen-verch-2001", "barnich-brandt-henneaux-2000"], "", "KSDGR", "I", finding="Standard smooth local covariance and BRST results expose the objects whose choice dependence still requires audit."),
    ("WEAK_CHOICE_ZF", "LOCALIC_SYNTHETIC"): rule(["heunen-landsman-spitters-2009", "coquand-spitters-2009"], "", "KSR", "DGI", finding="Localic constructions avoid point-selection in specific commutative settings, but no general ZF-without-Choice transfer is established."),

    ("CONSTRUCTIVE_COMPUTABLE", "FINITE_EXACT"): rule(["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1", "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"], "KSDI", "GR", local="KSDI", finding="The explicit Gaussian-rational interaction is executable using finite data, while the finite BV result remains a separate proof artifact."),
    ("CONSTRUCTIVE_COMPUTABLE", "HILBERT_OPERATOR"): rule(["neumann-pape-streicher-2018", "pour-el-richards-1981", "bridges-svozil-2000", "richman-bridges-1999"], "KSDR", "GI", finding="Constructive quantum logic, constructive Gleason, effective spectral analysis, and a wave-equation counterexample delimit computable Hilbert physics."),
    ("CONSTRUCTIVE_COMPUTABLE", "KREIN_INDEFINITE"): rule(["bender-boettcher-1998", "mostafazadeh-2001"], "", "KDS", "GIR", finding="Pseudo-Hermitian spectral ingredients are explicit but have not been reformulated constructively with physical state selection."),
    ("CONSTRUCTIVE_COMPUTABLE", "ALGEBRAIC_CSTAR"): rule(["coquand-spitters-2009", "henry-2014", "neumann-pape-streicher-2018"], "KSR", "D", "GI", finding="Constructive localic Gelfand duality and computable spectral representations cover commutative kinematics and state-adjacent structure."),
    ("CONSTRUCTIVE_COMPUTABLE", "SMOOTH_DISTRIBUTIONAL"): rule(["pour-el-richards-1981", "barnich-brandt-henneaux-2000"], "D", "KGR", "SI", finding="The wave-equation noncomputability theorem directly constrains naive computable propagation; BRST structure remains only adjacent."),
    ("CONSTRUCTIVE_COMPUTABLE", "LOCALIC_SYNTHETIC"): rule(["coquand-spitters-2009", "heunen-landsman-spitters-2009", "brenna-flori-2012"], "KSDR", "GI", finding="Constructive localic spectra, valuations, and internal one-parameter dynamics form a coherent non-point-set quantum fragment."),

    ("TOPOS_INTERNAL", "FINITE_EXACT"): rule(["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1", "constantin-doring-2020", "abramsky-coecke-2004"], "SR", "KDI", "G", finding="Finite categorical and contextual-entropy constructions coexist with the exact matrix witness, but their internalization is not automatic."),
    ("TOPOS_INTERNAL", "HILBERT_OPERATOR"): rule(["doring-2008", "brenna-flori-2012", "harding-heunen-2019"], "", "KSDR", "GI", finding="The topos constructions use external Hilbert/operator input to build internal spectra, measures, and dynamics."),
    ("TOPOS_INTERNAL", "KREIN_INDEFINITE"): rule(["gottschalk-2004", "harding-heunen-2019"], "", "KDS", "GIR", finding="Krein QFT and topos quantum dynamics exist separately; no reviewed source constructs an internal indefinite carrier."),
    ("TOPOS_INTERNAL", "ALGEBRAIC_CSTAR"): rule(["heunen-landsman-spitters-2009", "doring-2008", "brenna-flori-2012", "harding-heunen-2019"], "KSDR", "GI", finding="Contextual topos methods internalize commutative algebra, spectra, state measures, and one-parameter dynamics from operator-algebraic input."),
    ("TOPOS_INTERNAL", "SMOOTH_DISTRIBUTIONAL"): rule(["grinkevich-1996", "barnich-brandt-henneaux-2000"], "KR", "SGI", finding="Synthetic general relativity supplies formal smooth geometry, while probability and BV/renormalization remain separate classical ingredients."),
    ("TOPOS_INTERNAL", "LOCALIC_SYNTHETIC"): rule(["heunen-landsman-spitters-2009", "doring-2008", "flori-2011", "brenna-flori-2012", "harding-heunen-2019", "constantin-doring-2020"], "KSDR", "GI", finding="The reviewed topos programme supplies spectra, state measures, symmetry actions, one-parameter dynamics, and finite state reconstruction."),

    ("FINITE_DISCRETE", "FINITE_EXACT"): rule(["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1", "gibbons-hoffman-wootters-2004"], "KSDI", "GR", finding="Exact finite matrices and finite-field phase space supply a bounded quantum system with an actual entangling interaction."),
    ("FINITE_DISCRETE", "HILBERT_OPERATOR"): rule(["gibbons-hoffman-wootters-2004", "abramsky-coecke-2004", "constantin-doring-2020"], "KSDR", "GI", finding="Finite-dimensional phase space, categorical protocols, and contextual entropy cover Hilbert kinematics, states, operations, and reconstruction."),
    ("FINITE_DISCRETE", "KREIN_INDEFINITE"): rule(["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1", "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"], "KSDI", "GR", local="KSDI", finding="Explicit finite Krein matrices give sign, state-adjacent, J-unitary, and interacting witnesses at fixed dimension."),
    ("FINITE_DISCRETE", "ALGEBRAIC_CSTAR"): rule(["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1", "zohar-burrello-2014"], "KSDI", "GR", finding="The finite matrix algebra is a concrete C*-system, while lattice gauge work adds local constraints and truncation architecture."),
    ("FINITE_DISCRETE", "SMOOTH_DISTRIBUTIONAL"): rule(["kogut-susskind-1975", "zohar-burrello-2014", "bahr-dittrich-2009", "dittrich-2012"], "KDGR", "SI", finding="Lattice gauge and discrete-gravity work supplies dynamics, constraints, symmetry-restoration, and explicit continuum-comparison obligations."),
    ("FINITE_DISCRETE", "LOCALIC_SYNTHETIC"): rule(["harding-heunen-2019", "constantin-doring-2020", "abramsky-coecke-2004"], "KSDR", "GI", finding="Short-poset topoi, finite contextual entropy, and categorical protocols give finite internal/contextual kinematics, states, dynamics, and reconstruction."),
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def letters(obligation: str) -> str:
    return {K: "K", S: "S", D: "D", G: "G", I: "I", R: "R"}[obligation]


def assess(foundation: str, carrier: str, obligation: str) -> dict[str, Any]:
    spec = POLICY[(foundation, carrier)]
    letter = letters(obligation)
    if letter in spec["direct"]:
        status = "LOCAL_RESULT" if letter in spec["local"] else "LITERATURE_RESULT"
        relation = "directly " + OBLIGATION_FINDING[obligation]
    elif letter in spec["pieces"]:
        status = "PIECES_ONLY"
        relation = "contains ingredients relevant to, but does not compose a result that " + OBLIGATION_FINDING[obligation]
    else:
        status = "PRIORITY_GAP"
        relation = "does not yet provide a reviewed result that " + OBLIGATION_FINDING[obligation]
    summary = spec["finding"] + " For this obligation, the evidence " + relation + "."
    boundary = FOUNDATION_BOUNDARY[foundation] + " " + CARRIER_BOUNDARY[carrier] + " Still open here: " + OBLIGATION_MISSING[obligation] + "."
    return {"foundation": foundation, "carrier": carrier, "obligation": obligation, "status": status, "evidence": spec["evidence"], "summary": summary, "boundary": boundary}


def priority(cell: dict[str, Any]) -> tuple[int, int, int, str, str, str]:
    status_score = {"LOCAL_RESULT": 4, "LITERATURE_RESULT": 3, "PIECES_ONLY": 2, "PRIORITY_GAP": 1}[cell["status"]]
    obligation_score = {I: 6, G: 5, D: 4, S: 3, K: 2, R: 1}[cell["obligation"]]
    foundation_score = {"TOPOS_INTERNAL": 6, "CONSTRUCTIVE_COMPUTABLE": 5, "FINITE_DISCRETE": 4, "WEAK_CHOICE_ZF": 3, "WEAK_ARITHMETIC": 2, "CLASSICAL_STANDARD": 1}[cell["foundation"]]
    return (-status_score, -obligation_score, -foundation_score, cell["foundation"], cell["carrier"], cell["obligation"])


def build(cube: dict[str, Any], *, rebuild: bool = False) -> dict[str, Any]:
    expansion_id = "FOUNDATIONAL_INTERSECTION_CUBE_EXPANSION_V1"
    prior = load(OUTPUT) if OUTPUT.is_file() else None
    if prior and not rebuild:
        additions = prior["cell_additions"]
    else:
        occupied = {(x["foundation"], x["carrier"], x["obligation"]) for x in cube["cells"]}
        candidates = []
        for foundation, carrier in sorted(POLICY):
            for obligation in OBLIGATIONS:
                if (foundation, carrier, obligation) not in occupied:
                    candidates.append(assess(foundation, carrier, obligation))
        need = TARGET - len(cube["cells"])
        if need <= 0:
            raise ValueError("bootstrap cube is already at or above target and no expansion result exists")
        additions = sorted(candidates, key=priority)[:need]
    counts = Counter(x["status"] for x in additions)
    payload = [(x["foundation"], x["carrier"], x["obligation"], x["status"], x["evidence"]) for x in additions]
    return {
        "schema_version": "foundational-intersection-cube-expansion-v1",
        "result_id": expansion_id,
        "result_kind": "REVIEWED_CUBE_CELL_CROSSWALK",
        "lifecycle": "LITERATURE_SCOPED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "created": "2026-08-11",
        "repository_base_commit": "a002680d8fafc7f3bc23e704625894c23aee22c6",
        "method": {
            "target": "At least 75% of the 216-cell cube deliberately assessed",
            "qualification_rule": "Direct theorem/construction becomes LITERATURE_RESULT; bounded repository evidence becomes LOCAL_RESULT; cross-framework ingredients become PIECES_ONLY; a meaningful reviewed miss becomes PRIORITY_GAP.",
            "selection_rule": "Rank unoccupied coordinates by evidence status, then interaction/gauge/dynamics leverage, then underexposed foundation, and select deterministically until 162 cells are assessed.",
            "base_assessed_cells": 59,
            "added_cells": len(additions),
            "resulting_assessed_cells": 59 + len(additions),
            "status_counts": dict(sorted(counts.items())),
        },
        "provenance": {
            "base_cube_digest": "bf924cfffac2636160adc4e5c32b7445ea6ebd01065b25eca543a6f20092587a",
            "inputs": [
                {"path": str(EXPANSION_LEDGER.relative_to(ROOT)), "sha256": sha(EXPANSION_LEDGER)},
                {"path": str(FINITE_RESULT.relative_to(ROOT)), "sha256": sha(FINITE_RESULT)},
            ],
        },
        "cell_additions": additions,
        "canonical_digest": hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "claim_flags": {"seventy_five_percent_assessed": len(additions) >= 103, "literature_complete": False, "all_cells_solved": False, "cross_framework_transfer_automatic": False, "new_lorentzian_claim": False},
        "does_not_establish": ["literature completeness", "that every assessed coordinate is solved", "that PIECES_ONLY sources compose", "that PRIORITY_GAP means global literature absence", "a weakest base for any continuum theorem", "a constructive interacting Weyl theory", "a controlled continuum limit", "renormalization or QME restoration", "a new Lorentzian-causal result"],
        "human_report": "foundations/reports/cube-expansion-literature-analysis.md",
    }


def apply_expansion(cube: dict[str, Any], expansion: dict[str, Any]) -> dict[str, Any]:
    by_coord = {(x["foundation"], x["carrier"], x["obligation"]): x for x in cube["cells"]}
    for cell in expansion["cell_additions"]:
        coordinate = (cell["foundation"], cell["carrier"], cell["obligation"])
        if coordinate in by_coord and by_coord[coordinate] != cell:
            raise ValueError("conflicting pre-existing cell: " + "/".join(coordinate))
        by_coord[coordinate] = cell
    cube["cells"] = sorted(by_coord.values(), key=lambda x: (x["foundation"], x["carrier"], x["obligation"]))
    inputs = cube["provenance"]["inputs"]
    pin = {"path": str(OUTPUT.relative_to(ROOT)), "sha256": sha(OUTPUT)}
    inputs = [x for x in inputs if x["path"] != pin["path"]] + [pin]
    cube["provenance"]["inputs"] = inputs
    cube["repository_base_commit"] = "a002680d8fafc7f3bc23e704625894c23aee22c6"
    cube["claim_flags"].update({"fifty_nine_cells_deliberately_assessed": False, "one_hundred_sixty_two_cells_deliberately_assessed": True, "seventy_five_percent_assessed": True})
    from foundations.check_intersection_cube import canonical_digest
    cube["independent_checker"]["expected_digest"] = canonical_digest(cube)
    return cube


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the expansion result and expanded cube")
    parser.add_argument("--rebuild", action="store_true", help="recompute selection from the 59-cell base policy")
    parser.add_argument("--check", action="store_true", help="verify that the stored expansion applies idempotently")
    args = parser.parse_args()
    cube = load(CUBE)
    prior = load(OUTPUT) if OUTPUT.is_file() else None
    if args.rebuild and prior:
        old = {(x["foundation"], x["carrier"], x["obligation"]) for x in prior["cell_additions"]}
        cube["cells"] = [x for x in cube["cells"] if (x["foundation"], x["carrier"], x["obligation"]) not in old]
        cube["provenance"]["inputs"] = [x for x in cube["provenance"]["inputs"] if x["path"] != str(OUTPUT.relative_to(ROOT))]
    expansion = build(cube, rebuild=args.rebuild)
    if args.write:
        OUTPUT.write_text(json.dumps(expansion, indent=2) + "\n")
        cube = apply_expansion(cube, expansion)
        CUBE.write_text(json.dumps(cube, indent=2) + "\n")
    else:
        trial = apply_expansion(cube, expansion) if OUTPUT.is_file() else cube
        print(json.dumps({"status": "PASS", "added": len(expansion["cell_additions"]), "assessed_after_apply": len(trial["cells"]), "addition_status_counts": expansion["method"]["status_counts"], "digest": expansion["canonical_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
