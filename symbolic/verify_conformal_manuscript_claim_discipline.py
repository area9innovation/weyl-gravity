#!/usr/bin/env python3
"""Guard the referee-driven claim discipline of the archival manuscript.

This is an editorial regression check, not a mathematical certificate and
not a declaration that the manuscript is submission-ready.  The paper split
is checked separately; public artifact release and independent specialist
review remain external gates in ``notes/conformal-referee-major-revision.md``.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "07-08-conformal-residual-cohomology-archive.tex"


def words(tex: str) -> int:
    text = re.sub(r"%.*", " ", tex)
    text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^]]*\])?", " ", text)
    text = re.sub(r"[$\\{}\[\]&_^~]", " ", text)
    return len(re.findall(r"[A-Za-z0-9+-]+", text))


def between(source: str, start: str, end: str) -> str:
    if start not in source or end not in source.split(start, 1)[1]:
        raise AssertionError(f"missing manuscript delimiters: {start!r}, {end!r}")
    return source.split(start, 1)[1].split(end, 1)[0]


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[PASS]", label)


def main() -> None:
    source = PAPER.read_text(encoding="utf-8")
    abstract = between(source, r"\begin{abstract}", r"\end{abstract}")
    conclusion = between(
        source,
        r"\section{Conclusion}\label{sec:conclusion}",
        r"\appendix",
    )
    claim_boundary = between(
        source,
        r"\paragraph{Claim boundary.}",
        "No statement in this paper establishes",
    )
    quantum_outlook = between(
        source,
        r"\paragraph{Separate quantum local-algebra status.}",
        r"\paragraph{Vertex versus dynamics.}",
    )

    abstract_words = words(abstract)
    conclusion_words = words(conclusion)
    outlook_words = words(quantum_outlook)
    check("abstract remains within 250--350 words", 250 <= abstract_words <= 350)
    check("conclusion remains at most 350 words", conclusion_words <= 350)
    check("separate quantum outlook remains at most 180 words", outlook_words <= 180)
    check("claim boundary says eight and contains eight items", "Eight statements" in claim_boundary and claim_boundary.count(r"\item") == 8)
    check("literal quad and ambiguous pi=1 defects remain absent", ",quad" not in source and " pi=1" not in source)
    check("abstract foregrounds selected fixed-cylinder and Hadamard boundaries", "not the\nfixed-cylinder quantization" in abstract and "not a\nHadamard" in abstract)
    check("main theorems state invariant positive signature", source.count(r"\operatorname{sig}G") >= 4)
    check("survivors are named residual vertex/deformation classes", source.count("residual vertex/deformation classes") >= 3)
    check("classical BV data are distinguished from the free state representation", r"\paragraph{Classical BV data and the free state representation.}" in source)
    check(
        "authorship records the sole technical model author and non-technical orchestrator",
        r"\author{GPT-5.6.sol" in source
        and "Asger Alstrup Palm" in source
        and "non-technical orchestrator" in source
        and "claims no technical contribution" in source,
    )

    print(
        "MANUSCRIPT CLAIM-DISCIPLINE GUARDS: ALL PASS "
        f"(abstract={abstract_words}, conclusion={conclusion_words}, outlook={outlook_words})"
    )
    print("SUBMISSION GATES STILL OPEN: public archival release, independent specialist review")


if __name__ == "__main__":
    main()
