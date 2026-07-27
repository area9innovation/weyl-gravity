# Team note: what to investigate and clean up

Date: 27 July 2026
Audience: classical and quantum teams
Status: findings and requests, no scientific promotion or demotion

A publication-readiness pass over the whole tree turned up four things worth
your attention. Two are scientific questions only you can answer. Two are
cleanup. One is a process hazard that will keep biting us.

Nothing here changes a claim, a lifecycle state, or a certificate payload.

---

## 1. Twenty-two verification rails are broken. Please tell us which matter.

**This is the most consequential finding.**

The subtree extraction rewrote every commit id and stripped the
`physics/symplectic-reconstruction/` path prefix. Verifiers that do
git-attached provenance lookups —

```
git show <OLD_COMMIT>:physics/symplectic-reconstruction/<path>
```

— now fail on both halves. Of 30 scripts referencing a dangling commit or the
old prefix, **22 fail**: 17 on git-attached lookups, 2 on content
supersession, 3 on an import path that masks the same git-attached failure.

They live in `quantum-weyl/`, `closed_universe_observers/`,
`d_quotient_classical/`, `bridge/`, `paper/`, and `residual_atlas/`. Full list
and per-script failure mode:
`reports/standalone-history-crosswalk-2026-07-27.md`.

Stated plainly: **any claim whose only rail is one of these is currently
unverifiable in this repository.** That is not the same as wrong — the
mathematics is untouched — but we cannot presently demonstrate it, and an
external reviewer will find this quickly.

**What we need from you.** Two things, and the first is more important than
the second:

1. **Triage by load-bearing-ness.** Which of the 22 back a claim that is
   currently promoted in a paper or a lifecycle state? Those need repair
   before anything else. Which back scaffolding or superseded work? Those can
   be retired instead of repaired, which is cheaper and more honest.
2. **Approve a repair approach.** The mapping is already solved: 244 of 245
   dangling commits are resolved in `reports/standalone-history-crosswalk.json`
   (the one holdout pins `lib/math/ivtaylor.forge` in the external tango/forge
   repo and was never in this subtree). Rebuild with
   `ci/standalone_history_crosswalk.py`; check it with `--check`.

   We deliberately did **not** rewrite the pinned ids in place. That would
   edit historical provenance records, which the append-only law forbids, and
   several pins sit inside certificates whose own hashes are pinned
   downstream, so an in-place rewrite could cascade. The intended repair is a
   small shared helper that translates an old id through the crosswalk **at
   lookup time**, leaving the historical pin exactly as written:

   ```python
   # sketch, not yet written
   def attached_blob(old_commit, old_path):
       """Read a pinned blob, translating pre-extraction provenance."""
       new_commit, new_path = crosswalk.resolve(old_commit, old_path)
       return git_show(new_commit, new_path)
   ```

   That is a change to scientific verification code across ~22 files. It
   should be one person's coherent commit, not twenty-two scattered edits.

---

## 2. Five certificates pin a superseded input. Do their results survive?

Independent of the extraction, and **not** a provenance repair.

`closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json`
now hashes to `78cdd185…`. `certificate_graph/certificate-dag.json` agrees.
But five older certificates still pin the superseded `e2c9aad2…`:

- `BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json`
- `BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json`
- `COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1.json`
- `PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1.json`
- `POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json`

The superseded content genuinely exists in history (commits `0d246be9f5f6`
and `3a4de3ab1a90`), so this is the fail-closed machinery working exactly as
designed: an input changed and its dependents were never revisited.

**Please do not repin these to make the red go away.** The question is
whether each result still holds against the *current* input. If it does,
repin and say so. If it does not, the result changes. Either outcome is fine;
silently repinning is not.

The same family is why `paper/verify_09_relational_clocks_claim_map.py` fails
on `import hash drift` against
`planning/events/observer-phase1-relational-observable-disposition-synthesis-DONE-4623f01f99cc5526.json`.
That failure predates today's work and is deliberately left open.

---

## 3. Process hazard: a bibliography edit silently breaks five rails

Worth internalising, because it cost real time today and will recur.

Adding DOI links — touching nothing but `\bibitem` blocks — invalidated
manuscript-hash pins bound by claim maps for **Papers 10, 12, 14, 15 and 16**,
plus a planning overlay. All five passed at `HEAD` and failed after the edit.
Paper 12 additionally pins its *compiled PDF* hash, so it breaks on any
rebuild whatsoever.

**Rule: after any manuscript touch-up, re-run the claim-map generators**
(`paper/generate_*_claim_map.py`), then the verifiers. Do not assume an
editorial change is inert.

Two related traps:

- **Papers 11 must be built from the repository root**, not from `paper/`,
  because it `\input`s a root-relative path. Building it from `paper/` fails
  *and deletes the tracked PDF*.
- **Verifiers needing `sympy` must run under the mise Python**
  (`~/.local/share/mise/installs/python/latest/bin/python3`). The default
  `python3` fails at import — which is a failure, not a pass.

Worth someone's time: a cheap pre-commit or CI rail that recomputes every
`path`/`sha256` pin in `paper/*.json` and fails on drift. It runs in seconds
and would have caught all of this at the point of edit.

---

## 4. Bibliography cleanup — editorial, needs domain judgement

Both are per-paper editorial calls, which is why they were not guessed at.

**54 bibitems are never cited** across 17 papers (`07-08-archive` 6, `06` 6,
`13` 6, `14` 6, `11` 5, `00` 4, `03` 4, …). Encouragingly, the reverse never
happens: **every `\cite` in the series resolves** — zero cited-but-undefined
keys.

Most of the 54 are foundational works the paper plainly rests on but never
explicitly cites — Bach, Regge–Wheeler, Lee–Wald, Stelle, BV. For those the
fix is *a citation in the text*, not deletion. Deciding where each belongs
requires knowing what the argument actually leans on.

**11 bibitems state no title at all** (author, journal, volume, page only):
`02:BM2008PRL`, `02:BM2008PRD`, `03:BM2008PRL`, `03:Mostafazadeh2010`,
`03:vN1939`, `03:Holdom`, `04:Stelle`, `04:Holdom`, `04:Riegert`,
`17:stucker2024`, `17:gajicwarnick2024`. Each is cited *with* its full title
elsewhere in the series, so this is transcription, not research.

Once both are cleared, add a bibliography-hygiene rail. One is not added now
because the tree would fail it immediately, and a rail expected to fail is
not a rail.

---

## Already done — please don't redo it

- **Repository licensed.** CC BY 4.0 for manuscripts/certificates/data/docs,
  MIT for code. See `LICENSE`.
- **Publication model decided: GitHub only.** No arXiv, no journal, no release
  tag, no DOI. This follows from the authorship — the manuscripts name a model
  as principal author, which the major venues do not accept, and the
  attribution is not being restated to fit them. Cite a commit hash to fix a
  version. Rationale in `TODO.md`; reopen only if the attribution itself is
  reconsidered.
- **Dead citations repaired.** 22 `companion paper, 2026` bibitems in Papers
  01–06 plus unlocated entries in 08, 11, 13 now carry authors, exact titles,
  paper numbers, in-repo paths, and the repo URL. Five references to release
  tags that never existed in this repository are gone.
- **References verified.** Bibliography link coverage 65% → 93%. Every DOI was
  resolved against CrossRef with strict title/year/volume/page agreement, and
  two *book-review* false matches were caught and rejected. All 115 arXiv ids
  were checked against the arXiv API: **114 correct, one wrong** — Paper 07
  cited arXiv:1804.05602 (Altaş–Tekin, *Chiral Gravity*) for the *generic
  gravity in AdS* paper, which is arXiv:1705.10234, PRD 97 024028. Fixed; the
  archive and Paper 13 already had it right.
- **ABHT is genuine**, not a fabricated citation. Anderson–Bateman–Herzog–Turok,
  cited as "to appear" in refs [25] and [27] of arXiv:2607.00096, which we
  already cite as `BT2026`. Still unpublished; the entry now says so.
- **Standalone-history crosswalk built** — see item 1.

---

## Suggested order

1. Triage the 22 broken rails by whether a promoted claim depends on them
   (item 1). This gates how urgent the rest is.
2. Decide the five superseded pins (item 2) — scientific, cannot be delegated.
3. Add the pin-drift rail (item 3) so we stop re-creating the problem.
4. Bibliography cleanup (item 4) whenever there is a quiet slot.

Items 1 and 2 are the two where an external reviewer would say the archive
does not currently support its own claims. Items 3 and 4 are housekeeping.

Receipts for everything above:
`reports/standalone-history-crosswalk-2026-07-27.md`,
`reports/literature-and-reference-review-2026-07-27.md`,
`reports/publication-model-and-citation-repair-2026-07-27.md`,
`reports/release-gate-license-and-todo-restructure-2026-07-27.md`.
