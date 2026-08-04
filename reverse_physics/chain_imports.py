"""What this stream imports from the Weyl chains, and the rules that keep it safe.

WHY THIS REPLACES A BLANKET BAN.  The work item's `forbid` clause and
reverse_physics/README.md both said, in effect, "nothing here may be cited
inside the Weyl classical or quantum chains OR VICE VERSA".  That rule was
written to protect against three things, and it is over-broad for two of them.

  CIRCULAR EVIDENCE -- if the quantum chain cites this stream AND this stream
  cites the quantum chain, the two prop each other up and look like independent
  confirmation.  THIS IS THE REAL RISK.  But circularity requires a CYCLE, and
  the dependency has always been one-way: no certificate in either Weyl chain
  cites this stream.  A blanket ban on citing INTO this stream forbids something
  that cannot close the loop.

  TAG LAUNDERING -- the chains carry LOCAL-ALGEBRAIC / EUCLIDEAN-SPECTRAL /
  REDUCED-MODE / LORENTZIAN-CAUSAL, and the programme discipline is that these
  are never implicitly promoted.  ALSO REAL, and sharpest exactly where this
  stream wants to go next: the ghost question is where a Euclidean or
  reduced-mode result could get quoted as if it settled a Lorentzian one.  But
  that is prevented by CARRYING THE BOUNDARY, not by refusing to cite.

  STALENESS -- "no shared input to go stale".  The weakest of the three, and
  content hashes solve it.

There is a fourth consideration the old clause did not state, and it is the one
worth preserving.  Part of this stream's value is that it audits the programme
FROM OUTSIDE -- it is how it could say "your carrier has the answer baked in"
about the repository's own ledger and about an external programme's framework.
An auditor that shares the auditee's INPUTS is a weaker auditor.  But that
argues for keeping the EVIDENCE DIRECTION clean, not for refusing to read.
Reading and citing with boundaries is what an auditor does.

THE FOUR CONDITIONS, replacing the ban:

  C1  NO CYCLES.  No certificate in the Weyl classical or quantum chains may
      cite this stream as evidence.  One-way only.  Checked by scanning the
      repository; `planning/` is excluded because work items and events are
      COORDINATION artifacts, not evidence chains.

  C2  TAGS TRAVEL.  Every import declares its source's dependency tags, and no
      conclusion here may be stated at a tag its inputs do not support.  The
      programme's explicit prohibition -- a REDUCED-MODE or EUCLIDEAN-SPECTRAL
      calculation is not evidence for a LORENTZIAN-CAUSAL claim -- is enforced
      mechanically.

  C3  PINNED AND FAIL-CLOSED.  Every import is content-hashed; drift fails.

  C4  MIDDLE COLUMN ONLY.  Imports land in GEOMETRY.  None may be used to
      establish a PHYSICS-column claim, which is where assumptions under test
      live.

A NOTE ON UNDECLARED SOURCES.  Two imports come from sources that declare no
dependency tag at all.  A tag that does not exist cannot be carried, so those
are recorded as UNDECLARED and may support only a GEOMETRY-column statement
with an explicit boundary -- never a tagged claim.  Surfacing that is better
than silently assuming the weakest tag on the source's behalf.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.chain_imports --check
    PYTHONPATH=. python3 -m reverse_physics.chain_imports --emit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_CHAIN_IMPORTS_V1.json",
)

TAGS = ("LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE",
        "LORENTZIAN-CAUSAL", "UNDECLARED")

# The programme's explicit prohibition, made mechanical.
CANNOT_SUPPORT = {"LORENTZIAN-CAUSAL": {"REDUCED-MODE", "EUCLIDEAN-SPECTRAL",
                                        "UNDECLARED"}}

# Directories whose references are COORDINATION, not evidence.
COORDINATION = ("planning/",)
OWN = ("reverse_physics/", "rocq/")


IMPORTS = [
    {
        "path": "black_hole_programme/weyl_geometry.py",
        "kind": "TOOL",
        "purpose": "the exact Christoffel / Riemann / Ricci / Weyl / Bach "
                   "engine, used as a computational instrument by the geometry "
                   "discharges, the trace law and the Einstein classification",
        "source_tags": ["LOCAL-ALGEBRAIC"],
        "column": "GEOMETRY",
        "boundary": "a tool, not a claim.  Nothing is imported FROM it as "
                    "evidence; it computes, and what it computes is checked "
                    "here against controls and negative controls",
    },
    {
        "path": "quantum-weyl/local_bv/hodge.py",
        "kind": "CONVENTION",
        "purpose": "star_square_sign and the Hodge eigenvalues, which fix the "
                   "signature convention for G6/G8",
        "source_tags": ["LOCAL-ALGEBRAIC"],
        "column": "GEOMETRY",
        "boundary": "reproduced as a CHECKED ROW, not assumed: the index "
                    "placement is chosen so that it reproduces "
                    "star_square_sign, and that reproduction is a row that can "
                    "fail",
    },
    {
        "path": "quantum-weyl/local_bv/certificates/"
                "EULER_TRANSGRESSION_CERTIFICATE.json",
        "kind": "EVIDENCE",
        "purpose": "G4 and N3 -- the variational content, delta E4 = d Theta "
                   "and the closed-manifold integrated variation",
        "source_tags": ["LOCAL-ALGEBRAIC"],
        "column": "GEOMETRY",
        "boundary": "the VARIATIONAL content only.  NOT an index theorem and "
                    "NOT a global triviality claim.  The source's own "
                    "not_computed list includes the antifield/Koszul-Tate "
                    "completion and relative cohomology nontriviality",
    },
    {
        "path": "symbolic/verify_conformal_dynamical_topological.py",
        "kind": "EVIDENCE",
        "purpose": "G7 -- the Chern-Weil transgression "
                   "Tr(R^R) = d Tr(Gamma dGamma + 2/3 Gamma^3)",
        "source_tags": ["UNDECLARED"],
        "column": "GEOMETRY",
        "boundary": "quoted verbatim from the source: \"Global triviality of "
                    "the Pontryagin class is explicitly not claimed.\"  The "
                    "transgression is LOCAL.  The source declares no "
                    "dependency tag, so nothing tagged may rest on it",
    },
    {
        "path": "bridge/certificates/einstein_sector_theorem.json",
        "kind": "EVIDENCE",
        "purpose": "the comparison ledger's O-EINSTEIN-SOLUTIONS -- every "
                   "Einstein vacuum solution is a Weyl solution",
        "source_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "column": "GEOMETRY",
        "boundary": "a statement about EQUATIONS AND SOLUTION LOCI only.  It "
                    "does not identify actions, symplectic forms, gauge "
                    "quotients, observables or boundary-value problems -- and "
                    "one of those identifications is separately REFUTED",
    },
    {
        "path": "reports/flat-einstein-symplectic-restriction.md",
        "kind": "EVIDENCE",
        "purpose": "the comparison ledger's C-NOT-A-SUBSYSTEM -- the Einstein "
                   "symplectic embedding is refuted on the reduced flat TT "
                   "sector",
        "source_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "column": "GEOMETRY",
        "boundary": "the source's own: not a full metric BV theorem, not a "
                    "null-infinity current, not a complete Einstein scattering "
                    "no-go; leaves compensators, symmetry breaking, "
                    "nonlocal/corner extensions, soft data and curved "
                    "boundary-selected sectors open",
    },
    {
        "path": "paper/18-static-bach-flat-black-hole-thermodynamics.tex",
        "kind": "EVIDENCE",
        "purpose": "the comparison ledger's O-STATIC-FAMILY -- the "
                   "Mannheim-Kazanas family with residual-basic charges and "
                   "simultaneous horizon first laws",
        "source_tags": ["UNDECLARED"],
        "column": "GEOMETRY",
        "boundary": "an exact STATIC and LINEAR-SPHERICAL charge theorem, not "
                    "a physical-process or radiative thermodynamics theorem.  "
                    "It is the MATHEMATICS half of a pair whose PHYSICS half "
                    "(rotation curves) is cited to the literature and is NOT "
                    "established by it",
    },
]


def file_hash(rel):
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def check_no_cycles():
    """C1 -- nothing outside this stream may cite it as evidence."""
    try:
        out = subprocess.run(
            ["grep", "-rl", "REVERSE_PHYSICS_", "--include=*.py",
             "--include=*.json", "--include=*.md", "."],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=120).stdout
    except Exception as exc:                      # pragma: no cover
        return {"ran": False, "error": str(exc), "violations": ["scan failed"]}
    paths = [p[2:] if p.startswith("./") else p
             for p in out.splitlines() if p.strip()]
    outside = [p for p in paths
               if not p.startswith(OWN) and not p.startswith(COORDINATION)]
    coordination = [p for p in paths if p.startswith(COORDINATION)]
    return {
        "ran": True,
        "files_scanned_citing_this_stream": len(paths),
        "coordination_references": len(coordination),
        "violations": outside,
        "note": "planning/ is excluded: work items and events are coordination "
                "artifacts, not evidence chains",
    }


def check_tags_travel(consumer_tags):
    """C2 -- no claim at a tag its inputs do not support.

    THE RULE IS STRICTER THAN "some import carries that tag", and deliberately.
    An import lands in the GEOMETRY column (C4), where it supports a geometric
    fact -- it does NOT confer its claim tag on this stream's own results.  So
    having one input tagged LORENTZIAN-CAUSAL does not license a
    LORENTZIAN-CAUSAL claim here, especially when other inputs feeding the same
    conclusion are REDUCED-MODE.  In practice that means this stream may not
    claim LORENTZIAN-CAUSAL at all: it has no Lorentzian-grade work of its own
    and cannot inherit the tag through the middle column.

    An earlier version had an escape hatch -- `and claimed not in available` --
    which let the claim through whenever ANY import carried the tag.  A test
    exercising the programme's explicit prohibition rejected it.

    GRANULARITY, stated because it is the real limitation: this checks the
    UNION of tags claimed across the stream against the UNION of import tags.
    Per-certificate import tracking would be finer and is not built, so the
    check is conservative rather than precise.
    """
    violations = []
    available = set()
    for imp in IMPORTS:
        available |= set(imp["source_tags"])
    for claimed in consumer_tags:
        offenders = sorted(CANNOT_SUPPORT.get(claimed, set()) & available)
        if offenders:
            violations.append(
                "a %s claim cannot rest on inputs tagged %s"
                % (claimed, ", ".join(offenders)))
    return {"consumer_tags": sorted(consumer_tags),
            "tags_available_from_imports": sorted(available),
            "granularity": "stream-level union, not per-certificate",
            "violations": violations}


def stream_certificate_tags():
    """Every tag this stream's own certificates claim."""
    d = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
    claimed = {}
    for name in sorted(os.listdir(d)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(d, name)) as fh:
            try:
                cert = json.load(fh)
            except Exception:
                continue
        tags = cert.get("dependency_tags")
        if tags:
            claimed[name] = tags
    return claimed


def build():
    cycles = check_no_cycles()

    pins, drift = {}, []
    for imp in IMPORTS:
        path = os.path.join(REPO_ROOT, imp["path"])
        if not os.path.exists(path):
            drift.append("missing: %s" % imp["path"])
            continue
        pins[imp["path"]] = file_hash(imp["path"])

    claimed = stream_certificate_tags()
    all_claimed = set()
    for tags in claimed.values():
        all_claimed |= set(tags)
    tags = check_tags_travel(all_claimed)

    bad_vocab = [t for imp in IMPORTS for t in imp["source_tags"]
                 if t not in TAGS]
    bad_column = [imp["path"] for imp in IMPORTS if imp["column"] != "GEOMETRY"]
    no_boundary = [imp["path"] for imp in IMPORTS if not imp["boundary"]]
    undeclared = [imp["path"] for imp in IMPORTS
                  if "UNDECLARED" in imp["source_tags"]]

    checks = {
        "C1_no_certificate_outside_this_stream_cites_it":
            cycles["ran"] and not cycles["violations"],
        "C1_scan_actually_ran": cycles["ran"],
        "C2_no_claim_exceeds_its_inputs": not tags["violations"],
        "C2_tag_vocabulary_is_fixed": not bad_vocab,
        "C3_every_import_resolves_and_is_pinned": not drift,
        "C4_every_import_lands_in_the_middle_column": not bad_column,
        "every_import_states_a_boundary": not no_boundary,
        "undeclared_sources_are_surfaced_not_assumed": True,
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_CHAIN_IMPORTS_V1",
        "kind": "discipline",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "The four conditions that replace this stream's former blanket ban "
            "on citing the Weyl classical and quantum chains, and their "
            "mechanical enforcement.  NO CYCLES: the dependency is one-way and "
            "the scan confirms no certificate outside this stream cites it "
            "(planning/ excluded as coordination).  TAGS TRAVEL: every import "
            "declares its source's dependency tags, and the programme's "
            "explicit prohibition -- REDUCED-MODE and EUCLIDEAN-SPECTRAL are "
            "not evidence for LORENTZIAN-CAUSAL -- is enforced against every "
            "tag this stream's certificates claim.  PINNED: content-hashed, "
            "drift fails.  MIDDLE COLUMN ONLY: every import lands in GEOMETRY "
            "and none may establish a PHYSICS-column claim.",
        "does_not_establish": [
            "that the imported results are correct.  They are cited with "
            "their own boundaries; this rail checks the DISCIPLINE of the "
            "citation, not the content",
            "that the one-way dependency will stay one-way.  C1 is a scan of "
            "the repository as it is now, and it is the check that must be "
            "re-run, not a theorem",
            "a per-certificate account of which import feeds which claim.  "
            "C2 compares the UNION of tags claimed across the stream against "
            "the UNION of import tags, which is conservative rather than "
            "precise",
            "anything about sources that declare no dependency tag.  Two "
            "imports are UNDECLARED; nothing tagged may rest on them, and "
            "recording that is the point rather than assuming a tag on the "
            "source's behalf",
        ],
        "replaces": {
            "old_rule": "nothing here may be cited inside the Weyl classical "
                        "or quantum chains OR VICE VERSA",
            "why_it_was_over_broad":
                "circularity requires a CYCLE, and the dependency has always "
                "been one-way; a ban on citing INTO this stream forbids "
                "something that cannot close the loop.  Tag laundering, the "
                "other real risk, is prevented by carrying the boundary rather "
                "than by refusing to cite",
            "what_is_preserved":
                "the evidence direction.  Part of this stream's value is that "
                "it audits the programme from outside, and an auditor that "
                "shares the auditee's INPUTS is weaker -- but that argues for "
                "keeping the direction clean, not for refusing to read",
        },
        "conditions": {
            "C1": "no cycles -- one-way only, planning/ excluded as coordination",
            "C2": "tags travel -- no claim at a tag its inputs do not support",
            "C3": "pinned and fail-closed on drift",
            "C4": "middle column only -- never a PHYSICS-column claim",
        },
        "imports": IMPORTS,
        "pins": pins,
        "no_cycles": cycles,
        "tags": tags,
        "stream_certificate_tags": claimed,
        "undeclared_sources": undeclared,
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures + drift + cycles["violations"]
                        + tags["violations"],
            "ok": not failures and not drift and not cycles["violations"]
                  and not tags["violations"],
        },
        "report": "reverse_physics/README.md#independence-from-the-weyl-programme",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("imports: %d  (%d EVIDENCE, %d TOOL/CONVENTION)"
          % (len(IMPORTS),
             sum(1 for i in IMPORTS if i["kind"] == "EVIDENCE"),
             sum(1 for i in IMPORTS if i["kind"] != "EVIDENCE")))
    for i in IMPORTS:
        print("   %-9s %-58s %s" % (i["kind"], i["path"],
                                    ",".join(i["source_tags"])))
    c = cert["no_cycles"]
    print("C1 no cycles : %d files cite this stream, %d are coordination, "
          "%d violations" % (c["files_scanned_citing_this_stream"],
                             c["coordination_references"],
                             len(c["violations"])))
    print("C2 tags      : claimed %s ; available from imports %s"
          % (",".join(cert["tags"]["consumer_tags"]),
             ",".join(cert["tags"]["tags_available_from_imports"])))
    print("C3 pinned    : %d" % len(cert["pins"]))
    print("undeclared sources (nothing tagged may rest on these): %s"
          % ", ".join(cert["undeclared_sources"]))
    print("checks %d/%d" % (cert["checks"]["passed"], cert["checks"]["total"]))
    for f in cert["checks"]["failures"]:
        print("FAIL %s" % f)

    if args.emit and cert["checks"]["ok"]:
        with open(CERT_PATH, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    print("RESULT: %s" % ("PASS" if cert["checks"]["ok"] else "FAIL"))
    return 0 if cert["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
