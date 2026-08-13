#!/usr/bin/env python3
"""Build the exact finite-operator audit closing ten previously unmapped cells."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
CORE = FOUNDATIONS / "results/FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1.json"
BORN = FOUNDATIONS / "results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1.json"
REPORT = FOUNDATIONS / "reports/finite-operator-ten-cell-closure.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def promotion(foundation: str, carrier: str, obligation: str, status: str, role: str, finding: str, boundary: str) -> dict[str, Any]:
    return {
        "coordinate": {"foundation": foundation, "carrier": carrier, "obligation": obligation},
        "prior_status": "NOT_MAPPED",
        "new_status": status,
        "evidence_role": role,
        "finding": finding,
        "boundary": boundary,
    }


def build() -> dict[str, Any]:
    core, born = load(CORE), load(BORN)
    if core.get("result_id") != "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1":
        raise ValueError("finite interaction source identity")
    if born.get("result_id") != "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1" or born.get("interface", {}).get("status") != "CERTIFIED":
        raise ValueError("Born source identity")
    interaction_finding = "The named M_4(Q(i)) Hamiltonian H=Z tensor Z is a bounded operator on C^4, is not a sum of one-body terms, and exactly maps a product state to a state with reduced density I/2."
    interaction_boundary = "This is one finite two-qubit interaction, not a Weyl-gravity vertex, continuum interaction, scattering construction, or thermodynamic limit."
    promotions = [
        promotion("CLASSICAL_STANDARD", "HILBERT_OPERATOR", "INTERACTION_CONSTRUCTION", "LOCAL_RESULT", "DIRECT_LOCAL", interaction_finding, interaction_boundary),
        promotion("CONSTRUCTIVE_COMPUTABLE", "HILBERT_OPERATOR", "INTERACTION_CONSTRUCTION", "LOCAL_RESULT", "DIRECT_LOCAL", interaction_finding + " Every operation is a finite Gaussian-rational algorithm.", interaction_boundary),
        promotion("FINITE_DISCRETE", "HILBERT_OPERATOR", "INTERACTION_CONSTRUCTION", "LOCAL_RESULT", "DIRECT_LOCAL", interaction_finding, interaction_boundary),
        promotion("WEAK_CHOICE_ZF", "HILBERT_OPERATOR", "INTERACTION_CONSTRUCTION", "LOCAL_RESULT", "DIRECT_LOCAL", interaction_finding + " The labelled finite construction invokes no choice operation.", interaction_boundary),
        promotion("CLASSICAL_STANDARD", "KREIN_INDEFINITE", "INTERACTION_CONSTRUCTION", "LOCAL_RESULT", "DIRECT_LOCAL", "On the same finite carrier, J=Z tensor I and H=Z tensor Z satisfy H^sharp=H; the exact entangling evolution is therefore a genuine scoped Krein interaction.", interaction_boundary + " J-self-adjointness alone is not a physical-state or unitarity theorem."),
        promotion("WEAK_CHOICE_ZF", "KREIN_INDEFINITE", "INTERACTION_CONSTRUCTION", "LOCAL_RESULT", "DIRECT_LOCAL", "The labelled finite J and interaction H obey H^sharp=H by exact matrix arithmetic and require no choice operation.", interaction_boundary + " No infinite Krein completion is inferred."),
        promotion("CONSTRUCTIVE_COMPUTABLE", "KREIN_INDEFINITE", "STATE_REPRESENTATION", "LOCAL_RESULT", "DIRECT_LOCAL", "The explicit J-even finite corner P defines rho=P and omega_P(T)=Tr(PTP)/Tr(P); all entries and normalization are computable rationals.", "This represents a named finite companion-Hilbert positive state, not every Krein state or an interacting physical state."),
        promotion("CONSTRUCTIVE_COMPUTABLE", "KREIN_INDEFINITE", "PROBABILITY_RULE", "LOCAL_RESULT", "DIRECT_LOCAL", "For the certified finite Krein process fixture, the computable corner rule yields exact probabilities 9/25, 16/25, and 0, summing to one.", "The rule is conditional on the five finite-corner hypotheses and is not an unconditional probability rule for arbitrary Krein operators."),
        promotion("FINITE_DISCRETE", "HILBERT_OPERATOR", "COUNTERTERM_CLASSIFICATION", "LOCAL_RESULT", "DIRECT_LOCAL", "For the declared two-qubit parity P=Z tensor Z, the sixteen Pauli words form a complete Hermitian operator basis and exactly eight commute with P; these eight span every parity-preserving Hermitian correction.", "This is a complete counterterm-space classification only for the fixed finite two-qubit model and declared parity, not for Weyl gravity, locality, power counting, or a continuum limit."),
        promotion("FINITE_DISCRETE", "HILBERT_OPERATOR", "RENORMALIZED_PRODUCTS", "PIECES_ONLY", "SUPPORTING", "All 256 products of Pauli basis operators close exactly up to phases in {1,-1,i,-i}; finite-cutoff products and traces are therefore defined without coincident-point singularities.", "A regulated finite product is only an ingredient. No subtraction prescription, regulator-independent limit, microlocal extension, or continuum renormalized product is constructed."),
    ]
    if len(promotions) != 10 or len({tuple(item["coordinate"].values()) for item in promotions}) != 10:
        raise ValueError("ten-coordinate closure")
    value = {
        "schema_version": "foundational-finite-operator-ten-cell-closure-v1",
        "result_id": "FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1",
        "result_kind": "SCOPED_MULTI_CELL_LOCAL_CERTIFICATE",
        "lifecycle": "SUFFICIENCY_PROVED",
        "created": "2026-08-13",
        "repository_base_commit": "64e0e9460b659b43eb10583aa9d95fb27f2b5589",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Which ten currently unmapped intersections can be classified by exact finite-operator constructions without importing continuum, Choice, or Lorentzian conclusions?",
        "answer": "Ten emitted NOT_MAPPED cells can be classified. Six receive a genuine finite interaction under Hilbert or Krein realizations, two receive a constructive finite-corner state representation and probability rule, one receives a complete parity-preserving correction-space classification for the fixed two-qubit model, and one receives only a pieces-level regulated-product result. Nine are LOCAL_RESULT and one is PIECES_ONLY. Every conclusion remains scoped to named finite matrices.",
        "carrier_realization": {
            "finite_exact": "M_4(Q(i)) as labelled Gaussian-rational arrays",
            "hilbert_operator": "the same matrices acting boundedly on C^4 with the standard positive product",
            "krein_indefinite": "the same carrier with [x,y]=<x,Jy>, J=Z tensor I, and A^sharp=J A^* J",
            "relation": "EXACT_FINITE_REALIZATION",
            "non_equivalence_boundary": "This exact realization of one named finite algebra does not identify the general FINITE_EXACT, HILBERT_OPERATOR, and KREIN_INDEFINITE carrier classes.",
        },
        "promotions": promotions,
        "exact_witness": {
            "arithmetic": "EXACT_GAUSSIAN_RATIONAL",
            "hilbert_dimension": 4,
            "operator_basis": [a + " tensor " + b for a in ("I", "X", "Y", "Z") for b in ("I", "X", "Y", "Z")],
            "operator_basis_dimension": 16,
            "hilbert_schmidt_gram_diagonal": 4,
            "interaction": {
                "H": "Z tensor Z",
                "test_observable": "X tensor I",
                "derivation_value": "i[H,X tensor I]=-2 Y tensor Z",
                "entangled_output_reduced_density": "I/2",
            },
            "krein": {
                "J": "Z tensor I=diag(1,1,-1,-1)",
                "J_squared": "I",
                "H_sharp": "H",
            },
            "counterterms": {
                "declared_symmetry": "P=Z tensor Z",
                "all_hermitian_pauli_words": 16,
                "parity_even_basis_count": 8,
                "parity_even_basis": ["I tensor I", "I tensor Z", "Z tensor I", "Z tensor Z", "X tensor X", "X tensor Y", "Y tensor X", "Y tensor Y"],
            },
            "regulated_products": {
                "basis_products_checked": 256,
                "allowed_phases": ["1", "-1", "i", "-i"],
                "continuum_renormalized_product": False,
            },
            "constructive_krein_state": {
                "corner": "P_in=diag(1,0,0)",
                "formula": "omega_P(T)=Tr(PTP)/Tr(P)",
                "probabilities": ["9/25", "16/25", "0"],
                "sum": "1",
            },
        },
        "proof_obligations": [
            {"id": "SOURCE_CLOSURE", "status": "PASS", "evidence": "The finite interaction and finite-corner interface sources are content pinned."},
            {"id": "EXACT_CARRIER_REALIZATION", "status": "PASS", "evidence": "Every Gaussian-rational 4x4 matrix defines a bounded operator on C^4, and J supplies the displayed finite Krein product."},
            {"id": "NONTRIVIAL_INTERACTION", "status": "PASS", "evidence": "The commutator derivation is nonzero and the exact output has one-qubit reduction I/2."},
            {"id": "KREIN_INTERACTION", "status": "PASS", "evidence": "J^2=I and H^sharp=H are exact identities."},
            {"id": "CONSTRUCTIVE_STATE_AND_PROBABILITY", "status": "PASS", "evidence": "The finite corner is normalized and yields exact nonnegative probabilities summing to one."},
            {"id": "FINITE_COUNTERTERM_COMPLETENESS", "status": "PASS", "evidence": "Pauli trace orthogonality proves a complete 16-word Hermitian basis; exactly eight words commute with the declared parity."},
            {"id": "REGULATED_PRODUCT_CLOSURE", "status": "PASS", "evidence": "All 256 Pauli word products close exactly up to a Gaussian-unit phase."},
            {"id": "TEN_PRIOR_EMPTY_COORDINATES", "status": "PASS", "evidence": "Cube-v7 verification independently requires all ten prior v6 statuses to be NOT_MAPPED."},
            {"id": "RENORMALIZATION_BOUNDARY", "status": "PASS", "evidence": "The regulated-product cell is only PIECES_ONLY; no continuum renormalization flag is promoted."},
        ],
        "proof_authority": {
            "status": "INDEPENDENT_EXACT_REDERIVATION",
            "meaning": "The checker reconstructs Pauli matrices over exact Gaussian rationals, their operator basis, the interaction and Krein identities, the parity commutant, all basis products, and the rational Born fixture without calling either source producer.",
        },
        "provenance": {
            "inputs": [
                {"path": str(CORE.relative_to(ROOT)), "sha256": sha(CORE), "role": "finite interaction model and carrier typing"},
                {"path": str(BORN.relative_to(ROOT)), "sha256": sha(BORN), "role": "certified finite-corner state and probability rule"},
            ]
        },
        "independent_checker": {
            "path": "foundations/check_finite_operator_ten_cell_closure.py",
            "expected_digest": "80ae23dbd42ef9a0947bfca14a44bc02260d6f0211bf50a7f2755d7c520f77d8",
            "checks": ["source identities and hashes", "ten unique target coordinates", "Pauli trace orthogonality", "nonzero entangling interaction", "Krein adjoint", "parity counterterm basis", "256 regulated products", "exact finite-corner probabilities", "claim boundaries"],
        },
        "claim_flags": {
            "exactly_ten_previously_unmapped_cells_classified": True,
            "nine_local_results": True,
            "one_pieces_only_result": True,
            "finite_hilbert_interaction_constructed": True,
            "finite_krein_interaction_constructed": True,
            "constructive_krein_state_probability_constructed": True,
            "fixed_model_counterterm_space_classified": True,
            "finite_regulated_products_constructed": True,
            "continuum_renormalized_products_constructed": False,
            "weyl_counterterms_classified": False,
            "general_carrier_equivalence_established": False,
            "choice_principle_required": False,
            "empirical_agreement_assessed": False,
            "lorentzian_claim": False,
        },
        "does_not_establish": [
            "equivalence of finite exact, Hilbert, and Krein carrier classes beyond the named finite realization",
            "an infinite-dimensional or continuum interacting theory",
            "a Weyl-gravity or Bateman--Turok interaction vertex",
            "Weyl counterterm or anomaly classification",
            "a continuum renormalized product or regulator-independent limit",
            "QME restoration or residual quantum transfer",
            "a general constructive probability rule for arbitrary Krein processes",
            "a weakest mathematical base or reverse-mathematics lower bound",
            "causal propagation, empirical agreement, or a LORENTZIAN-CAUSAL result",
        ],
        "human_report": "foundations/reports/finite-operator-ten-cell-closure.md",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = [
        "# Exact finite-operator closure of ten empty cells",
        "",
        f"**Result:** `{value['result_id']}`",
        "",
        "**Lifecycle:** `SUFFICIENCY_PROVED`",
        "",
        "**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`",
        "",
        "## Outcome",
        "",
        value["answer"],
        "",
        "This audit exploits an exact relation that the earlier migration pass did not",
        "yet certify: the labelled Gaussian-rational matrices are simultaneously finite",
        "arrays, bounded operators on the named finite Hilbert space, and—after adding",
        "the displayed `J`—operators on a named finite Krein space. This is an",
        "object-level realization, not an equivalence of carrier categories.",
        "",
        "## Ten coordinate decisions",
        "",
        "| # | Coordinate | New status | Exact reason | Boundary |",
        "|---:|---|---|---|---|",
    ]
    for index, item in enumerate(value["promotions"], 1):
        coordinate = item["coordinate"]
        key = " × ".join((coordinate["foundation"], coordinate["carrier"], coordinate["obligation"]))
        lines.append(f"| {index} | `{key}` | `{item['new_status']}` | {item['finding']} | {item['boundary']} |")
    lines.extend([
        "",
        "## Exact controls",
        "",
        "The independent checker reconstructs all sixteen two-qubit Pauli words over",
        "Gaussian rationals. Their Hilbert--Schmidt Gram matrix is `4 I`, so they form",
        "a complete operator basis. The interaction has",
        "`i[Z tensor Z, X tensor I]=-2 Y tensor Z`, and its displayed finite-time",
        "output has reduced density `I/2`. With `J=Z tensor I`, it also satisfies",
        "`H^sharp=H`.",
        "",
        "Exactly eight Pauli words commute with the declared parity `P=Z tensor Z`;",
        "they span every parity-preserving Hermitian correction in this fixed model.",
        "All 256 basis products close up to `1,-1,i,-i`. That latter fact is deliberately",
        "graded `PIECES_ONLY`: cutoff products do not become continuum renormalized",
        "products by a change of vocabulary.",
        "",
        "The constructive Krein corner independently reproduces probabilities",
        "`9/25`, `16/25`, and `0`, with sum one.",
        "",
        "## Verification",
        "",
        "```text",
        "python3 foundations/build_finite_operator_ten_cell_closure.py --check",
        "python3 foundations/check_finite_operator_ten_cell_closure.py",
        "python3 foundations/verify_finite_operator_ten_cell_closure.py",
        "python3 -m unittest foundations.tests.test_finite_operator_ten_cell_closure",
        "```",
        "",
        "## Boundaries",
        "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]],
        "",
    ])
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
