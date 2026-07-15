#!/usr/bin/env python3
"""Editorial guards for the split conformal-gravity publications.

These checks enforce the referee-driven publication architecture.  They do
not certify the mathematical identities; the theorem rail and independent
checkers do that separately.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
MONOLITH = PAPER / "07-08-conformal-residual-cohomology-archive.tex"
PAPER_A = PAPER / "07-conformal-residual-cohomology-krein.tex"
PAPER_B = PAPER / "08-conformal-covariant-causal-transport.tex"
SUPPLEMENT = PAPER / "07-08-conformal-residual-cohomology-computational-supplement.tex"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[PASS]", label)


def segment(source: str, start: str, end: str) -> str:
    check(f"source contains {start}", start in source)
    tail = source.split(start, 1)[1]
    check(f"source contains {end} after {start}", end in tail)
    return tail.split(end, 1)[0]


def exact_count(source: str) -> int:
    return len(re.findall(r"\bexact\b", source, flags=re.IGNORECASE))


def main() -> None:
    paths = (MONOLITH, PAPER_A, PAPER_B, SUPPLEMENT)
    check("all four publication entrypoints exist", all(path.is_file() for path in paths))
    sources = {path.name: path.read_text(encoding="utf-8") for path in paths}
    monolith = sources[MONOLITH.name]
    paper_a = sources[PAPER_A.name]
    paper_b = sources[PAPER_B.name]
    supplement = sources[SUPPLEMENT.name]

    derived = segment(
        monolith,
        r"\label{thm:derived-residual-reduction}",
        r"\begin{remark}[Fixed cylinder and relative alternatives]",
    )
    check("derived-reduction theorem now has an explicit proof", r"\begin{proof}" in derived and r"\end{proof}" in derived)
    for dependency in (
        "prop:Taub-constraint",
        "eq:moment-Taub-target",
        "prop:dual-endpoint",
        "eq:zero-mode-transgression",
        "eq:tau-equals-theta",
        "eq:residual-BFV-charge",
        "eq:CE-differential",
    ):
        check(f"derived proof cites {dependency}", dependency in derived)

    check("Paper A is a compact standalone entrypoint", paper_a.count("\n") < 900)
    check("Paper B is a compact standalone entrypoint", paper_b.count("\n") < 1000)
    check("Paper A contains its focused ledger", r"\section{Focused claim ledger}" in paper_a)
    check("Paper B contains its focused ledger", r"\section{One-page claim ledger}" in paper_b)
    check("Paper A proves rather than declares derived reduction", r"\begin{theorem}[Derived residual reduction]" in paper_a and r"\begin{proof}" in segment(paper_a, r"\begin{theorem}[Derived residual reduction]", r"\begin{remark}[Fixed-cylinder alternative]"))
    check("Paper A does not claim a causal propagator", "does not use reduced-mode or Euclidean evidence to claim a Lorentzian\noff-shell BV propagator" in paper_a)
    check("Paper B imports rather than recomputes residual CE", "We do not repeat that Chevalley--Eilenberg\ncalculation here" in paper_b and "no residual Chevalley--Eilenberg matrices" in paper_b)
    check("Paper B states the sourced constraint identity", r"\label{eq:sourced-subsidiary}" in paper_b)
    check("Paper B states the all-row causal identity", r"\label{eq:full-properties}" in paper_b and r"Q_{\rm prol}\Lambda_{{\rm prol},\pm}" in paper_b)
    check("article prose no longer overuses exact", exact_count(paper_a) <= 30 and exact_count(paper_b) <= 30)

    check("supplement is versioned rather than a scaffold", "versioned supplement" in supplement and "not an independent theorem\npaper yet" not in supplement and "will contain" not in supplement)
    check("supplement has separate A/B ledgers", "Paper A: residual cohomology and pairing" in supplement and "Paper B: covariant causal transport" in supplement)
    check("supplement documents isolated release audit", "audit_conformal_publication_release.py" in supplement and "git archive" in supplement)

    for name, source in sources.items():
        check(
            f"{name} records programme authorship",
            r"\author{GPT-5.6.sol" in source
            and "Asger Alstrup Palm" in source
            and "non-technical" in source,
        )

    print("CONFORMAL SPLIT-PUBLICATION EDITORIAL GUARDS: ALL PASS")


if __name__ == "__main__":
    main()
