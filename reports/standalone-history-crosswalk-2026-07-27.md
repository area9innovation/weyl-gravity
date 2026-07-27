# Standalone-history replay crosswalk

Date: 27 July 2026

## Scope

Closes the "finish the standalone-history replay crosswalk" release item. No
scientific claim, lifecycle state, certificate payload, or theorem changes. The
pass adds one derived artifact, one reproducible tool, and this receipt.

## The problem

This repository was extracted from a monorepo subtree. The extraction rewrote
every commit id and stripped the `physics/symplectic-reconstruction/` path
prefix. Provenance pins of the form

```
git show <OLD_COMMIT>:physics/symplectic-reconstruction/<path>
```

therefore resolve to nothing here. No `git filter-repo` mapping table survived
the split — there is no `.git/filter-repo/commit-map`, no grafts, and no
replace refs — so the old ids cannot be translated by lookup.

The earlier 2026-07-27 touch-up repaired six such pins for Papers 14 and 15 by
hand. This pass establishes the general mapping.

## Method

The pins are recoverable by content. Each one records the sha256 its blob is
expected to have, so:

1. strip the `physics/symplectic-reconstruction/` prefix from the pinned path;
2. walk the commits that touched that path in the filtered history;
3. find the commit whose blob at that path hashes to the recorded sha256.

That commit is the rewritten image of the old one. The derivation never
guesses: a pin whose recorded content appears nowhere is reported as
unresolved rather than approximated.

Pins are collected from two sources: JSON objects carrying a commit-ish key
alongside `path` and `sha256`, and Python module-level string constants
(parsed with `ast`, so multi-line implicit concatenation is handled).

## Result

| Quantity | Count |
| --- | ---: |
| Provenance pins examined | 858 |
| Pins whose commit still resolves | 2 |
| Distinct dangling commits | 245 |
| **Resolved to their standalone image** | **244** |
| Classified as external (tango/forge) | 1 |
| **Unresolved** | **0** |

The single external entry pins `lib/math/ivtaylor.forge`, which belongs to the
tango/forge substrate repository and was never part of this subtree. It is
correctly unresolvable here and is classified rather than reported as damage.

The crosswalk is `reports/standalone-history-crosswalk.json`. Each entry records
the new commit, the witness path before and after prefix stripping, the witness
content hash, and every site that cites the old id.

## Verifier rail

`ci/standalone_history_crosswalk.py` rebuilds the artifact; `--check`
re-derives it and fails if the committed copy drifted, so a stale or
hand-edited crosswalk cannot pass. Runtime is about 46 seconds.

Fail-closed behaviour was tested by mutating one `new_commit` to zeros:
`--check` exits 1. Restoring the file returns it to exit 0.

## Finding: 22 verifiers are broken by the extraction

This sweep also measured the damage, which had not previously been quantified.
Of 30 verifier and test scripts that reference either a dangling commit or the
old path prefix, **22 fail and 8 pass**:

| Failure class | Count |
| --- | ---: |
| Git-attached lookup against a dangling commit and/or the stripped path prefix | 17 |
| Content supersession drift (see below) | 2 |
| Other (module import path, dependent test suite) | 3 |

The "other" three are not a separate defect. Re-running one of them with
`PYTHONPATH` set to the repository root advances it past the import error to
the same git-attached failure.

These are live scientific verifiers in `quantum-weyl/`,
`closed_universe_observers/`, `d_quotient_classical/`, `bridge/`, `paper/`, and
`residual_atlas/`. A failing verifier is not a passing one: any claim resting
on these rails is currently unverifiable in this repository until they are
repaired.

**The repair is now mechanically determined** — the crosswalk supplies every
missing commit id, and the path fix is prefix stripping — but it is
deliberately not applied here. Rewriting the pinned ids in place would edit
historical provenance records, which this programme's append-only law forbids;
several of the pins also live inside certificates whose own content hashes are
pinned downstream, so an in-place rewrite could cascade. The correct repair is
for the verifiers to translate an old id through the crosswalk at lookup time,
leaving the historical pin as written. That is a change to scientific
verification code and is left for an explicit decision. Recorded as an open
item in `TODO.md`.

## Separate pre-existing finding: content supersession drift

Two failures are **not** extraction damage and the crosswalk does not address
them.

`closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json`
currently hashes to `78cdd185…`. `certificate_graph/certificate-dag.json` agrees.
But five older certificates still pin the superseded value `e2c9aad2…`:

- `BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json`
- `BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json`
- `COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1.json`
- `PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1.json`
- `POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json`

The superseded content does exist in the filtered history, at commits
`0d246be9f5f6` and `3a4de3ab1a90`, so this is a real supersession that
downstream pins did not follow — the fail-closed machinery working as designed.
Whether those five results survive the input change is a scientific question
about the results themselves, not a provenance repair, and is not decided here.

## Receipt

| Check | Command | Result |
| --- | --- | --- |
| Crosswalk derivation | `python3 ci/standalone_history_crosswalk.py` | 244 resolved, 1 external, 0 unresolved, 46 s |
| Crosswalk rail | `python3 ci/standalone_history_crosswalk.py --check` | PASS |
| Rail fails closed | mutate one `new_commit` to zeros, re-run `--check` | exit 1, restored to exit 0 |
| Verifier census | 30 candidates run under the mise Python, 180 s timeout each | 8 PASS / 22 FAIL |
| Artifact parses | `json.load` on the crosswalk | PASS |
| Whitespace | `git diff --check` on scoped paths | PASS |

Verifiers requiring `sympy` must run under the mise Python
(`~/.local/share/mise/installs/python/latest/bin/python3`); the default
`python3` fails at import, which is not a pass.

## Higher tiers

Tiers 2 and 3 were not run, and their omission is not a skipped pass. This pass
adds a derived provenance artifact and a tool; it changes no mathematical
input, shared operator, schema, certificate payload, or manuscript. The 22
failing verifiers were measured, not modified, and their failures predate this
pass.

## Does not establish

This crosswalk does not repair any verifier, does not restore any failing
check to passing, does not decide whether the five superseded pins above
invalidate their results, and does not recover the original monorepo commit
ids as objects — only their standalone images. It also does not certify that
858 pins is the complete set: pins expressed in forms neither source pattern
recognizes would not have been counted.
