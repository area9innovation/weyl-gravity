#!/usr/bin/env python3
"""Audit the programme introduction after covariant causal closure.

The audit has five jobs:

* require the completed residual and covariant theorem chains and qualifiers;
* keep the eight technical papers and their division of labour explicit;
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
SOURCE = ROOT / "paper" / "00-ghosts-geometry-reality.tex"
README = ROOT / "README.md"
JSON_REPORT = ROOT / "symbolic" / "programme-introduction-language-report.json"
TSV_REPORT = ROOT / "symbolic" / "programme-introduction-language-report.tsv"

SERIES_ENTRYPOINTS = (
    ("00", "00-ghosts-geometry-reality"),
    ("01", "01-symplectic-diagonalization"),
    ("02", "02-variational-fock"),
    ("03", "03-fourth-order-vacuum"),
    ("04", "04-fourth-order-gravity"),
    ("05", "05-interaction-obstructions"),
    ("06", "06-einstein-weyl-interaction-obstructions"),
    ("07", "07-conformal-residual-cohomology-krein"),
    ("08", "08-conformal-covariant-causal-transport"),
)

SHARED_PUBLICATION_ENTRYPOINTS = (
    "07-08-conformal-residual-cohomology-computational-supplement",
    "07-08-conformal-residual-cohomology-archive",
)

LEGACY_PAPER_BASENAMES = (
    "ghosts-geometry-reality",
    "symplectic-diagonalization",
    "variational-fock",
    "fourth-order-vacuum",
    "fourth-order-gravity",
    "interaction-obstructions",
    "einstein-weyl-interaction-obstructions",
    "conformal-residual-cohomology-krein",
    "conformal-covariant-causal-transport",
    "conformal-residual-cohomology-computational-supplement",
    "conformal-residual-cohomology",
)

NUMBERED_PAPER_ARTIFACT = re.compile(
    r"^(?:\d{2}|\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.(?:tex|pdf)$"
)
UNNUMBERED_SUPPORT_TEX = {"theorem_statements.tex"}


REQUIRED_SNIPPETS = {
    "Paper VII theorem": r"\begin{theorem}[Paper VII: selected residual state theorem]",
    "Paper VII theorem label": r"\label{thm:intro-paper-vii}",
    "polarized state complex": r"\mathcal H_{\rm state}",
    "centered classes": r"H^4_{\rm res}",
    "residual signature": r"\operatorname{sig}G_{\rm res}=(2,0)",
    "field Gram matrix": r"G_{\rm res}=I_2",
    "Paper VIII theorem": r"\begin{theorem}[Paper VIII: covariant causal transport]",
    "Paper VIII theorem label": r"\label{thm:intro-paper-viii}",
    "causal homotopy identity": r"Q\Lambda_\pm+\Lambda_\pm Q=1",
    "causal support": r"\operatorname{supp}(\Lambda_\pm f)",
    "covariant transport result": r"H^4_{\rm cov}\cong H^4_{\rm res}",
    "covariant signature": r"\operatorname{sig}G_{\rm cov}=(2,0)",
    "covariant Gram matrix": r"G_{\rm cov}=I_2",
    "status table": r"\label{tab:programme-status}",
    "series dependency diagram": r"\label{fig:dependency}",
    "VII--VIII relation diagram": r"\label{fig:vii-viii-relation}",
    "eight-paper series map": r"The eight technical papers have distinct jobs",
    "Paper VII computation": r"Paper~VII computes the selected residual state cohomology",
    "Paper VIII transport": r"Paper~VIII constructs the covariant causal bridge",
    "no duplicate CE calculation": r"Paper~VIII does not perform another Chevalley--Eilenberg calculation",
    "open frontier list": r"The genuine open problems are:",
    "Hadamard frontier": r"distributional and Hadamard completion",
    "integrated symmetry frontier": r"integration of the infinitesimal $\mathfrak{so}(4,2)$ action",
    "boundary frontier": r"alternative boundary, clock, relative, and deparametrized",
    "nonlinear frontier": r"nonlinear BV--BFV transfer and the higher Taub/Kuranishi maps",
    "interaction descent frontier": r"interaction descent for the two surviving deformation classes",
    "composite frontier": r"renormalized local composite representatives",
    "anomaly frontier": r"anomaly classification and a renormalized quantum master equation",
    "unitarity frontier": r"interacting probability and unitarity",
    "quantum challenge":
        r"Do the two classical deformation classes survive an anomaly-free"
        r" renormalized quantum BV--BFV transfer?",
}


REQUIRED_STATUS_ROWS = (
    "I--III & Positive/Krein free scalar geometry",
    "IV & Covariant local free gravity classification",
    "V--VI & Interaction deformation and obstruction",
    "VII & Absolute residual $H^4$ and Krein pairing",
    "VIII & Covariant causal BV--BFV transport",
)


TECHNICAL_PAPERS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")


STALE_OPEN_RULES = (
    (
        "causal-homotopy-construction",
        re.compile(
            r"(?:what remains|remaining|must|need(?:s|ed)?|required)[^.]{0,180}"
            r"construct(?:ion|ing)?[^.]{0,180}causal\s+(?:green\s+)?homotop"
            r"|construct(?:ion|ing)?[^.]{0,180}causal\s+(?:green\s+)?homotop"
            r"[^.]{0,100}(?:remain(?:s|ed)?\s+open|is\s+open)",
            re.IGNORECASE,
        ),
    ),
    (
        "causal-quasi-isomorphism",
        re.compile(r"causal\s+quasi-isomorphism[^.]{0,100}(?:remain|open|construct)", re.IGNORECASE),
    ),
    (
        "covariant-current-comparison",
        re.compile(r"compar(?:e|ison|ing)[^.]{0,180}covariant\s+green\s+current", re.IGNORECASE),
    ),
    (
        "covariant-pairing-comparison",
        re.compile(r"covariant(?:/cauchy|\s+and\s+cauchy)?\s+pairing[^.]{0,100}(?:remain|open|construct)", re.IGNORECASE),
    ),
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
        "pontryagin-space",
        re.compile(r"(?:the|this) (?:completed )?(?:space|module) is a pontryagin space", re.IGNORECASE),
        "The completed module is a Pontryagin space.",
    ),
    (
        "bounded-conformal-generators",
        re.compile(r"all (?:the )?conformal generators are bounded", re.IGNORECASE),
        "All conformal generators are bounded.",
    ),
    (
        "automatic-group-integration",
        re.compile(
            r"(?:the )?lie algebra representation (?:automatically )?integrates to (?:a |the )?(?:global )?so\(4,2\)",
            re.IGNORECASE,
        ),
        "The Lie algebra representation automatically integrates to a global SO(4,2) representation.",
    ),
    (
        "global-ghost-krein-metric",
        re.compile(
            r"(?:the )?centered ghost insertion is a (?:global )?nondegenerate krein metric",
            re.IGNORECASE,
        ),
        "The centered ghost insertion is a global nondegenerate Krein metric.",
    ),
    (
        "bounded-residual-brst",
        re.compile(r"(?:the )?residual brst differential is bounded", re.IGNORECASE),
        "The residual BRST differential is bounded.",
    ),
    (
        "covariant-metric-completion",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes) "
            r"(?:a |the )?covariant (?:metric-field )?(?:sobolev|distributional|hilbert|krein) completion",
            re.IGNORECASE,
        ),
        "The theorem establishes a covariant metric-field Sobolev completion.",
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
        "green-hyperbolic-completion",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes|constructs) "
            r"(?:a |the )?green-hyperbolic completion",
            re.IGNORECASE,
        ),
        "The theorem constructs a Green-hyperbolic completion.",
    ),
    (
        "curved-auxiliary-green-witness",
        re.compile(
            r"(?:the )?(?:ordinary-derivative )?auxiliary (?:realization|complex) "
            r"(?:now )?(?:supplies|gives|admits|proves) (?:a |the )?"
            r"(?:complete )?(?:local )?(?:all-degree )?(?:bv )?green(?:'s)? witness",
            re.IGNORECASE,
        ),
        "The auxiliary realization now supplies a complete all-degree BV Green witness.",
    ),
    (
        "auxiliary-causal-homotopies",
        re.compile(
            r"(?:the )?(?:formally self-adjoint )?(?:auxiliary )?witness "
            r"(?:supplies|gives|constructs) retarded and advanced green homotopies",
            re.IGNORECASE,
        ),
        "The auxiliary witness supplies retarded and advanced Green homotopies.",
    ),
    (
        "auxiliary-causal-quasi-isomorphism",
        re.compile(
            r"(?:the )?(?:ordinary-derivative )?auxiliary (?:realization|complex) "
            r"is causally quasi-isomorphic",
            re.IGNORECASE,
        ),
        "The auxiliary realization is causally quasi-isomorphic to the metric complex.",
    ),
    (
        "direct-same-bundle-factorization",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes|constructs) "
            r"(?:a |the )?direct same[- ]bundle (?:bach |metric )?factorization",
            re.IGNORECASE,
        ),
        "The theorem proves a direct same-bundle Bach factorization.",
    ),
    (
        "local-tt-projector",
        re.compile(r"(?:the )?tt projector is local", re.IGNORECASE),
        "The TT projector is local.",
    ),
    (
        "local-el-split",
        re.compile(r"(?:the )?(?:e/l|e--l) (?:branch )?split is local", re.IGNORECASE),
        "The E/L branch split is local.",
    ),
    (
        "raw-product-sobolev",
        re.compile(
            r"(?:the )?raw (?:fourth-order |bach )?(?:cauchy )?data (?:has|have|carry|carries) "
            r"(?:a |the )?(?:standard )?product sobolev norm",
            re.IGNORECASE,
        ),
        "The raw Bach Cauchy data carry a standard product Sobolev norm.",
    ),
    (
        "hadamard-state",
        re.compile(
            r"(?:the|this|our) (?:result|theorem) (?:proves|establishes|constructs) "
            r"(?:a |the )?hadamard state",
            re.IGNORECASE,
        ),
        "The theorem constructs a Hadamard state.",
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
    if term == "evidence for" and "not evidence for a stronger level" in lowered:
        return (
            "still-valid-scoped-condition",
            "The occurrence is an explicit dependency-boundary disclaimer.",
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
                "paperVIII",
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


def latex_section(text: str, title: str, *, level: str = "section") -> str:
    """Return a section body without interpreting TeX."""

    marker = rf"\{level}{{{title}}}"
    start = text.find(marker)
    if start < 0:
        return ""
    next_marker = "\\section{" if level == "section" else "\\subsection{"
    end = text.find(next_marker, start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def architecture_errors(text: str) -> list[str]:
    """Check the eight-paper split and the three noninterchangeable levels."""

    flat = normalize(text)
    lowered = flat.lower()
    errors: list[str] = []
    if not re.search(r"\beight(?:-paper| technical papers?)\b", lowered):
        errors.append("publication architecture: introduction must state eight technical papers")

    for paper_number in TECHNICAL_PAPERS:
        cited = re.search(
            rf"Paper(?:~|\s)+{paper_number}\b[^\n]{{0,120}}\\cite\{{paper{paper_number}}}",
            text,
        )
        if not cited:
            errors.append(
                f"publication architecture: missing cited companion description for Paper {paper_number}"
            )

    vii_window_match = re.search(r"Paper(?:~|\s)+VII\b", text)
    vii_window = "" if vii_window_match is None else normalize(
        text[vii_window_match.start():vii_window_match.start() + 900]
    ).lower()
    if "comput" not in vii_window or "residual" not in vii_window:
        errors.append("paper split: Paper VII must explicitly compute residual cohomology")

    viii_window_match = re.search(r"Paper(?:~|\s)+VIII\b", text)
    viii_window = "" if viii_window_match is None else normalize(
        text[viii_window_match.start():viii_window_match.start() + 1100]
    ).lower()
    if "transport" not in viii_window or "covariant" not in viii_window or "causal" not in viii_window:
        errors.append("paper split: Paper VIII must explicitly transport the covariant causal complex")
    if not re.search(
        r"Paper(?:~|\s)+VIII[^.]{0,220}(?:does not|doesn't|without)[^.]{0,160}(?:recompute|another Chevalley--Eilenberg)",
        flat,
        re.IGNORECASE,
    ):
        errors.append("paper split: Paper VIII must explicitly disclaim a second CE computation")

    levels_match = re.search(r"three logically distinct levels", flat, re.IGNORECASE)
    levels_window = "" if levels_match is None else normalize(
        flat[levels_match.start():levels_match.start() + 2400]
    ).lower()
    for level_name, terms in (
        ("local", ("local free", "local bv", "local dynamics")),
        ("residual", ("residual reduction", "residual gauge", "residual brst")),
        ("interaction", ("interaction stability", "interacting")),
    ):
        if not any(term in levels_window for term in terms):
            errors.append(f"conceptual levels: missing explicit {level_name} level")
    if "must not be conflated" not in levels_window:
        errors.append("conceptual levels: must explicitly say that the three levels are not conflated")

    reductions_match = re.search(r"three reductions remain conceptually distinct", flat, re.IGNORECASE)
    reductions_window = "" if reductions_match is None else flat[
        reductions_match.start():reductions_match.start() + 900
    ].lower()
    for carrier in (
        "covariant metric bv complex",
        "cauchy/energy one-particle complex",
        "polarized residual state complex",
    ):
        if carrier not in reductions_window:
            errors.append(f"conceptual reductions: missing carrier {carrier}")

    open_section = latex_section(text, "What remains open")
    if not open_section:
        errors.append("open frontier: missing What remains open section")
    else:
        open_flat = normalize(open_section)
        open_sentences = re.split(r"(?<=[.!?])\s+", open_flat)
        for sentence in open_sentences:
            if "no longer open" in sentence.lower():
                continue
            for rule, pattern in STALE_OPEN_RULES:
                match = pattern.search(sentence)
                if match:
                    errors.append(f"stale Paper-VIII open item: {rule} ({match.group(0)})")
        frontier_requirements = (
            ("distributional/Hadamard completion", r"(?:distributional|Hadamard)"),
            ("integrated SO(4,2) representation", r"integration[^.]{0,120}(?:so\(4,2\)|representation)"),
            ("alternative boundary/clock/deparametrization", r"alternative boundary[^.]{0,120}(?:clock|deparametr)"),
            ("nonlinear BV--BFV and higher Taub/Kuranishi", r"nonlinear BV--BFV[^.]{0,120}(?:Taub|Kuranishi)"),
            ("interaction descent", r"interaction descent"),
            ("renormalized local composites", r"renormalized local composite"),
            ("anomalies/QME", r"anomaly[^.]{0,120}quantum master equation"),
            ("interacting probability/unitarity", r"interacting probability[^.]{0,80}unitarity"),
        )
        for label, pattern in frontier_requirements:
            if not re.search(pattern, open_flat, re.IGNORECASE):
                errors.append(f"open frontier: {label} must remain explicit")

    stale_global = (
        "Curved auxiliary witness/covariant pairing/Hadamard completion & Open",
        "Forked dependency structure of the seven technical papers",
    )
    for stale in stale_global:
        if stale in text:
            errors.append(f"stale introduction metadata remains: {stale}")
    return errors


def readme_errors(text: str) -> list[str]:
    """Keep the repository landing page synchronized with Papers I--VIII."""

    flat = normalize(text)
    errors: list[str] = []
    if "one expository introduction and eight technical papers" not in flat:
        errors.append("README metadata: expected one introduction plus eight technical papers")
    paper_dir = ROOT / "paper"
    for number, basename in SERIES_ENTRYPOINTS:
        if not re.search(rf"\| {number} \|[^\n]*{re.escape(basename)}\.tex", text):
            errors.append(f"README metadata: missing numbered {number} row for {basename}")
        for suffix in (".tex", ".pdf"):
            if not (paper_dir / f"{basename}{suffix}").is_file():
                errors.append(f"paper naming: missing {basename}{suffix}")
    for basename in SHARED_PUBLICATION_ENTRYPOINTS:
        for suffix in (".tex", ".pdf"):
            if not (paper_dir / f"{basename}{suffix}").is_file():
                errors.append(f"paper naming: missing shared artifact {basename}{suffix}")
    for basename in LEGACY_PAPER_BASENAMES:
        for suffix in (".tex", ".pdf"):
            if (paper_dir / f"{basename}{suffix}").exists():
                errors.append(f"paper naming: obsolete unnumbered artifact remains: {basename}{suffix}")
    for path in paper_dir.iterdir():
        if not path.is_file() or path.suffix not in {".tex", ".pdf"}:
            continue
        if path.name in UNNUMBERED_SUPPORT_TEX:
            continue
        if not NUMBERED_PAPER_ARTIFACT.fullmatch(path.name):
            errors.append(f"paper naming: top-level publication artifact lacks a two-digit prefix: {path.name}")
    if re.search(r"\| 7[AB] \|", text):
        errors.append("README metadata: obsolete 7A/7B numbering remains")
    if "**Paper 7** (the residual state-side theorem)" not in text:
        errors.append("README narrative: missing Paper 7 state-side role")
    if "**Paper 8** (the covariant field-side theorem)" not in text:
        errors.append("README narrative: missing Paper 8 covariant role")
    if "rather than recomputing the Chevalley--Eilenberg complex" not in flat:
        errors.append("README narrative: Paper 8 must disclaim recomputing residual CE cohomology")
    return errors


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
    errors.extend(architecture_errors(text))
    return errors


def build_report(text: str) -> tuple[dict[str, object], list[str]]:
    occurrences = audit_language(text)
    citations = citation_audit(text)
    overclaims = overclaim_violations(text)
    errors = structural_errors(text)
    landing_errors = readme_errors(README.read_text(encoding="utf-8"))
    errors.extend(landing_errors)
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
            "selected closed-cylinder free programme: residual BV-BFV state "
            "cohomology with Krein-Fock completion and pairing-compatible "
            "covariant causal metric transport"
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
        "publication_architecture": {
            "technical_papers": list(TECHNICAL_PAPERS),
            "introduction_errors": architecture_errors(text),
            "readme_errors": landing_errors,
        },
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
    for rule, _pattern, fixture in OVERCLAIM_RULES:
        triggered = {item["rule"] for item in overclaim_violations(text + "\n" + fixture)}
        if rule not in triggered:
            failures.append(f"guard fixture did not trigger: {rule}")

    paper_rows = "\n".join(
        f"Paper~{number} \\cite{{paper{number}}} has its stated role."
        for number in TECHNICAL_PAPERS
    )
    architecture_fixture = f"""
The eight technical papers form one programme.
{paper_rows}
Three logically distinct levels follow.
Level 1 is local free dynamics. Level 2 is residual gauge reduction.
Level 3 is interaction stability. These levels must not be conflated.
Three reductions remain conceptually distinct: the covariant metric BV complex,
the Cauchy/energy one-particle complex, and the polarized residual state complex.
Paper~VII computes residual cohomology.
Paper~VIII transports the covariant causal complex.
Paper~VIII does not perform another Chevalley--Eilenberg calculation.
\\section{{What remains open}}
Distributional and Hadamard completion remains open.
Integration of the infinitesimal so(4,2) action to a representation remains open.
Alternative boundary, clock, and deparametrized polarizations remain open.
Nonlinear BV--BFV transfer and higher Taub/Kuranishi maps remain open.
Interaction descent remains open.
Renormalized local composites remain open.
Anomaly classification and the quantum master equation remain open.
Interacting probability and unitarity remain open.
\\section{{Conclusion}}
"""
    valid_errors = architecture_errors(architecture_fixture)
    if valid_errors:
        failures.append(f"valid architecture fixture failed: {'; '.join(valid_errors)}")
    architecture_mutations = (
        (
            "eight-technical-papers",
            architecture_fixture.replace("eight technical papers", "seven technical papers"),
            "publication architecture",
        ),
        (
            "Paper-VII-computes",
            architecture_fixture.replace("Paper~VII computes", "Paper~VII summarizes"),
            "Paper VII must explicitly compute",
        ),
        (
            "Paper-VIII-transports",
            architecture_fixture.replace("Paper~VIII transports", "Paper~VIII describes"),
            "Paper VIII must explicitly transport",
        ),
        (
            "Paper-VIII-does-not-recompute",
            architecture_fixture.replace(
                "Paper~VIII does not perform another Chevalley--Eilenberg calculation.",
                "Paper~VIII recomputes the Chevalley--Eilenberg calculation.",
            ),
            "must explicitly disclaim a second CE computation",
        ),
        (
            "three-level-distinction",
            architecture_fixture.replace("must not be conflated", "may be conflated"),
            "must explicitly say that the three levels are not conflated",
        ),
        (
            "three-reduction-carriers",
            architecture_fixture.replace(
                "the Cauchy/energy one-particle complex",
                "an unspecified middle complex",
            ),
            "conceptual reductions: missing carrier",
        ),
        (
            "stale-Paper-VIII-open-item",
            architecture_fixture.replace(
                "Distributional and Hadamard completion remains open.",
                "Constructing causal Green homotopies remains open. Hadamard completion remains open.",
            ),
            "stale Paper-VIII open item",
        ),
    )
    for name, fixture, expected in architecture_mutations:
        fixture_errors = architecture_errors(fixture)
        if not any(expected in error for error in fixture_errors):
            failures.append(f"architecture guard fixture did not trigger: {name}")
    for valid_name in ("09-future-paper.tex", "10-future-paper.pdf", "07-08-shared-supplement.tex"):
        if not NUMBERED_PAPER_ARTIFACT.fullmatch(valid_name):
            failures.append(f"paper naming guard rejected valid future name: {valid_name}")
    for invalid_name in ("9-future-paper.tex", "future-paper.tex", "paper-10-future.pdf"):
        if NUMBERED_PAPER_ARTIFACT.fullmatch(invalid_name):
            failures.append(f"paper naming guard accepted invalid name: {invalid_name}")
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
        print(
            "introduction guard fixtures:",
            f"{len(OVERCLAIM_RULES) + 7 - len(guard_failures)}/"
            f"{len(OVERCLAIM_RULES) + 7} PASS",
        )

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
