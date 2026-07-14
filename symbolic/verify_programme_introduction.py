#!/usr/bin/env python3
"""Audit the programme introduction after the classical BV--BFV closure.

The audit has four jobs:

* require the completed classical theorem chain and its category qualifiers;
* classify every formerly dangerous conditional-language occurrence;
* verify that every citation key is defined; and
* fail closed on affirmative analytic, nonlinear, quantum, particle, or
  boundary-universal overclaims.

Use ``--write-report`` after an intentional manuscript revision and
``--check-report`` in CI.  ``--guards`` runs synthetic expected-failure
fixtures through the same overclaim detector used on the manuscript.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "ghosts-geometry-reality.tex"
JSON_REPORT = ROOT / "symbolic" / "programme-introduction-language-report.json"
TSV_REPORT = ROOT / "symbolic" / "programme-introduction-language-report.tsv"


REQUIRED_SNIPPETS = {
    "classical algebraic theorem":
        r"\begin{theorem}[Classical algebraic pure-Weyl BV--BFV theorem]",
    "theorem label": r"\label{thm:intro-pure-weyl}",
    "minimal BV/raw theorem":
        r"\mathcal C_{\rm raw}^{\rm tf,min}\oplus\mathcal C_{\rm tr}",
    "trace acyclicity": r"H(\mathcal C_{\rm tr})=0",
    "bulk-to-state subsection":
        r"\subsection{From bulk BV fields to residual states}",
    "endpoint duality": r"I/\operatorname{im}C\cong(\ker A)^*",
    "normalized suspension": r"\boxed{\tau=\Theta,\qquad\lambda=+1.}",
    "polarized state complex":
        r"\operatorname{Sym}(\mathcal W_+\oplus\mathcal W_-) "
        r"\otimes\Lambda^\bullet\mathfrak{so}(4,2)^*",
    "centered classes":
        r"H^4_{\rm res}=\operatorname{span}\{[W_+^2],[W_-^2]\}",
    "field Gram matrix": r"G_{\rm res}=I_2",
    "status table": r"\label{tab:programme-status}",
    "solid theorem-chain diagram": r"\label{fig:pure-weyl-chain}",
    "historical gap closed": r"That historical gap is now closed",
    "analytic frontier": r"\subsection{Analytic completion}",
    "nonlinear frontier": r"\subsection{Nonlinear classical extension}",
    "quantum frontier": r"\subsection{Quantum extension}",
    "quantum challenge":
        r"Do the two classical deformation classes survive an anomaly-free"
        r" renormalized quantum BV--BFV transfer?",
}


REQUIRED_STATUS_ROWS = (
    "Smooth BGG/deformation-complex bridge & Proved",
    "Metric-to-Weyl curvature isomorphism & Proved",
    "Explicit $E/A/L$ cylinder realization & Proved",
    "Minimal pure-Weyl BV/raw-chain identification & Proved",
    "Trace-sector contraction & Proved",
    "Gauge-fixed/nonminimal contraction & Proved",
    "Fifteen zero-mode preservation & Proved",
    "Endpoint duality & Proved",
    "Endpoint-to-Taub obstruction map & Proved",
    "BV-to-BFV suspension & Proved, $\\lambda=+1$",
    "Positive-frequency state ledger & Proved",
    "Strict residual CE transfer & Proved",
    "Two centered classes & Proved",
    "Field-induced Gram matrix $I_2$ & Proved",
    "Hilbert/Krein completion & Open",
    "Nonlinear stability & Open",
    "Quantum master equation/anomalies & Open",
    "Quantum survival of the two classes & Open",
    "Particle or $S$-matrix unitarity & Not claimed",
)


AUDIT_TERMS = (
    ("conditional", re.compile(r"\bconditional\b", re.IGNORECASE)),
    ("conjecture", re.compile(r"\bconjecture\b", re.IGNORECASE)),
    ("hypothesis", re.compile(r"\bhypothesis\b", re.IGNORECASE)),
    ("candidate", re.compile(r"\bcandidate\b", re.IGNORECASE)),
    ("evidence for", re.compile(r"\bevidence\s+for\b", re.IGNORECASE)),
    (
        "assuming the field-theoretic identification",
        re.compile(r"assuming\s+the\s+field-theoretic\s+identification", re.IGNORECASE),
    ),
    (
        "assuming no additional rows",
        re.compile(r"assuming\s+no\s+additional\s+(?:antifield\s+)?rows", re.IGNORECASE),
    ),
    (
        "expected BFV sector",
        re.compile(r"expected\s+BFV\s+sector", re.IGNORECASE),
    ),
    (
        "proposed zero-mode transfer",
        re.compile(r"proposed\s+zero-mode\s+transfer", re.IGNORECASE),
    ),
    (
        "intrinsic residual pairing only",
        re.compile(r"intrinsic\s+residual\s+pairing\s+only", re.IGNORECASE),
    ),
)


# These fixtures are affirmative claims that the introduction must reject.
# The regular expressions deliberately avoid the manuscript's explicit
# negations ("does not establish", "not claimed", and open questions).
OVERCLAIM_RULES = (
    (
        "hilbert-krein-completion",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes) "
            r"(?:a |the )?(?:completed )?(?:hilbert|krein)(?:/krein)? completion",
            re.IGNORECASE,
        ),
        "The theorem establishes a Hilbert/Krein completion.",
    ),
    (
        "nonlinear-classical-equivalence",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes) "
            r"(?:the )?nonlinear (?:stability|equivalence|extension)",
            re.IGNORECASE,
        ),
        "This result proves nonlinear stability.",
    ),
    (
        "interacting-bv-cohomology",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|computes|establishes) "
            r"(?:the )?interacting bv cohomology",
            re.IGNORECASE,
        ),
        "The theorem computes the interacting BV cohomology.",
    ),
    (
        "quantum-master-equation",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes) "
            r"(?:the )?(?:renormalized )?quantum master equation",
            re.IGNORECASE,
        ),
        "The result proves the quantum master equation.",
    ),
    (
        "weyl-anomaly-cancellation",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes|shows) "
            r"(?:the )?(?:absence|cancellation) of (?:the )?weyl anomaly",
            re.IGNORECASE,
        ),
        "The theorem proves cancellation of the Weyl anomaly.",
    ),
    (
        "quantum-survival",
        re.compile(
            r"(?:the )?two (?:classical )?(?:deformation )?classes "
            r"(?:survive|remain under) (?:quantization|renormalization)",
            re.IGNORECASE,
        ),
        "The two classical deformation classes survive quantization.",
    ),
    (
        "positive-graviton-space",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|provides|establishes) "
            r"(?:a )?positive graviton (?:fock|hilbert) space",
            re.IGNORECASE,
        ),
        "The result provides a positive graviton Fock space.",
    ),
    (
        "particle-unitarity",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes) "
            r"(?:full )?particle unitarity",
            re.IGNORECASE,
        ),
        "The theorem proves particle unitarity.",
    ),
    (
        "s-matrix-unitarity",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes) "
            r"(?:full )?s-matrix unitarity",
            re.IGNORECASE,
        ),
        "The theorem establishes S-matrix unitarity.",
    ),
    (
        "universal-boundary-choice",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) holds for "
            r"(?:all|every) boundary (?:condition|choice|problem)s?",
            re.IGNORECASE,
        ),
        "The theorem holds for all boundary conditions.",
    ),
    (
        "d-as-hamiltonian",
        re.compile(
            r"(?:the same|this|the) theorem (?:also )?(?:holds|applies|remains valid) "
            r"when \$?d\$? is (?:retained|treated) as (?:a |the )?(?:physical )?hamiltonian",
            re.IGNORECASE,
        ),
        "The same theorem holds when $D$ is retained as a physical Hamiltonian.",
    ),
)


def normalize(text: str) -> str:
    """Collapse whitespace for theorem and overclaim checks."""

    return re.sub(r"\s+", " ", text).strip()


def source_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_occurrence(term: str, context: str) -> tuple[str, str]:
    lowered = context.lower()
    if term == "conjecture" and (
        "resonance hierarchy" in lowered or "general $p{:}q$ rule" in lowered
    ):
        return (
            "still-valid-interaction-frontier",
            "The statement concerns the still-open general interaction hierarchy, not the closed Paper-VII bridge.",
        )
    if term == "hypothesis" and "earlier versions" in lowered and "now closed" in lowered:
        return (
            "historical-closed-gap",
            "The occurrence records the former field-theoretic hypothesis and explicitly marks it closed.",
        )
    if term == "conditional" and any(
        marker in lowered for marker in ("analytic", "nonlinear", "quantum", "historical")
    ):
        return (
            "still-valid-scoped-condition",
            "The condition is explicitly outside the completed classical algebraic category.",
        )
    return (
        "obsolete-or-unclassified",
        "This occurrence is not an approved historical or still-open use and requires revision.",
    )


def audit_language(text: str) -> list[dict[str, object]]:
    lines = text.splitlines()
    occurrences: list[dict[str, object]] = []
    for line_number, line in enumerate(lines, start=1):
        for term, pattern in AUDIT_TERMS:
            for match in pattern.finditer(line):
                lo = max(0, line_number - 3)
                hi = min(len(lines), line_number + 2)
                context = " ".join(part.strip() for part in lines[lo:hi])
                classification, rationale = classify_occurrence(term, context)
                occurrences.append(
                    {
                        "term": term,
                        "line": line_number,
                        "match": match.group(0),
                        "classification": classification,
                        "rationale": rationale,
                        "context": normalize(context),
                    }
                )
    return occurrences


def citation_audit(text: str) -> dict[str, object]:
    cited: set[str] = set()
    for match in re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", text):
        cited.update(key.strip() for key in match.group(1).split(",") if key.strip())
    defined = set(re.findall(r"\\bibitem\{([^}]+)\}", text))
    return {
        "cited_count": len(cited),
        "defined_count": len(defined),
        "undefined": sorted(cited - defined),
        "uncited_bibitems": sorted(defined - cited),
        "required_keys_present": {
            key: key in defined and key in cited
            for key in (
                "paperVII",
                "GoverPetersonIntro",
                "CapBGGIntro",
                "DneprovGrigorievIntro",
                "CattaneoMnevReshetikhinIntro",
            )
        },
    }


def overclaim_violations(text: str) -> list[dict[str, str]]:
    flat = normalize(text)
    violations: list[dict[str, str]] = []
    for rule, pattern, _fixture in OVERCLAIM_RULES:
        match = pattern.search(flat)
        if match:
            violations.append({"rule": rule, "match": match.group(0)})
    return violations


def structural_errors(text: str) -> list[str]:
    flat = normalize(text)
    errors: list[str] = []
    for name, snippet in REQUIRED_SNIPPETS.items():
        if normalize(snippet) not in flat:
            errors.append(f"missing required content: {name}")
    for row in REQUIRED_STATUS_ROWS:
        if normalize(row) not in flat:
            errors.append(f"missing theorem-status row: {row}")
    if r"\subsection{The remaining bridge}" in text:
        errors.append("obsolete subsection remains: The remaining bridge")
    for paper_number in ("I", "II", "III", "IV", "V", "VI", "VII"):
        if f"Paper {paper_number} \\cite" not in text:
            errors.append(f"missing companion-paper description: Paper {paper_number}")
    return errors


def build_report(text: str) -> tuple[dict[str, object], list[str]]:
    occurrences = audit_language(text)
    citations = citation_audit(text)
    overclaims = overclaim_violations(text)
    errors = structural_errors(text)
    errors.extend(
        f"obsolete language at line {item['line']}: {item['term']}"
        for item in occurrences
        if item["classification"] == "obsolete-or-unclassified"
    )
    errors.extend(f"undefined citation: {key}" for key in citations["undefined"])
    errors.extend(
        f"required citation is not both cited and defined: {key}"
        for key, present in citations["required_keys_present"].items()
        if not present
    )
    errors.extend(
        f"overclaim guard triggered: {item['rule']} ({item['match']})"
        for item in overclaims
    )
    report: dict[str, object] = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_digest(text),
        "logical_category": (
            "quadratic D-finite SO(4)-finite algebraic closed-cylinder "
            "BV-BFV state complex with positive-frequency polarization"
        ),
        "language_occurrences": occurrences,
        "language_summary": {
            "total": len(occurrences),
            "historical_closed": sum(
                item["classification"] == "historical-closed-gap" for item in occurrences
            ),
            "still_valid": sum(
                str(item["classification"]).startswith("still-valid") for item in occurrences
            ),
            "obsolete_or_unclassified": sum(
                item["classification"] == "obsolete-or-unclassified" for item in occurrences
            ),
        },
        "citation_audit": citations,
        "overclaim_violations": overclaims,
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    return report, errors


def json_text(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def tsv_text(report: dict[str, object]) -> str:
    rows = ["term\tline\tclassification\tmatch\trationale"]
    for item in report["language_occurrences"]:
        cells = (
            str(item["term"]),
            str(item["line"]),
            str(item["classification"]),
            str(item["match"]),
            str(item["rationale"]),
        )
        rows.append("\t".join(cell.replace("\t", " ").replace("\n", " ") for cell in cells))
    return "\n".join(rows) + "\n"


def run_guard_fixtures(text: str) -> list[str]:
    failures: list[str] = []
    if overclaim_violations(text):
        failures.append("base manuscript already triggers an overclaim rule")
        return failures
    for rule, _pattern, fixture in OVERCLAIM_RULES:
        triggered = {item["rule"] for item in overclaim_violations(text + "\n" + fixture)}
        if rule not in triggered:
            failures.append(f"guard fixture did not trigger: {rule}")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--check-report", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    text = SOURCE.read_text(encoding="utf-8")
    report, errors = build_report(text)
    expected_json = json_text(report)
    expected_tsv = tsv_text(report)

    if args.guards:
        guard_failures = run_guard_fixtures(text)
        errors.extend(guard_failures)
        print(f"overclaim guard fixtures: {len(OVERCLAIM_RULES) - len(guard_failures)}/{len(OVERCLAIM_RULES)} PASS")

    if args.write_report:
        JSON_REPORT.write_text(expected_json, encoding="utf-8")
        TSV_REPORT.write_text(expected_tsv, encoding="utf-8")
        print("wrote", JSON_REPORT.relative_to(ROOT))
        print("wrote", TSV_REPORT.relative_to(ROOT))

    if args.check_report:
        if not JSON_REPORT.exists() or JSON_REPORT.read_text(encoding="utf-8") != expected_json:
            errors.append("JSON language report is missing or stale; run --write-report")
        if not TSV_REPORT.exists() or TSV_REPORT.read_text(encoding="utf-8") != expected_tsv:
            errors.append("TSV language report is missing or stale; run --write-report")

    if errors:
        for error in errors:
            print("FAIL:", error)
        raise SystemExit(1)

    summary = report["language_summary"]
    citations = report["citation_audit"]
    print(
        "language audit:",
        f"{summary['total']} occurrences;",
        f"historical={summary['historical_closed']};",
        f"still-valid={summary['still_valid']};",
        "obsolete=0",
    )
    print(
        "citation audit:",
        f"{citations['cited_count']} cited keys;",
        "undefined=0",
    )
    print("PROGRAMME INTRODUCTION AUDIT: ALL PASS")


if __name__ == "__main__":
    main()
