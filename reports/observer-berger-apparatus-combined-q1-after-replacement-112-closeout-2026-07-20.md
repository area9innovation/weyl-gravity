# Observer Berger apparatus combined q1 after replacement 112 close-out

The typed pushout is certified with 160 rows.  Its row count is derived from
the 168-row direct sum by eight independent semantic relations: two memories,
two multipliers and their cotangents.  All other 48 material rows remain
distinct.

The complete unary is the certified positive-mixed 112-row block plus six
real two-component \(D_K\) transport pairs.  Nilpotency, cyclicity, reality,
\(K_{\rm Berger}\) commutation, both embeddings, the quotient, full-rank odd
pairing and detector-smearing chain compatibility pass exactly.  The
coordinate-level response remains rank two.

CLOSE-OUT: DONE — the typed 160-row apparatus unary pushout is certified

EVIDENCE: `closed_universe_observers/certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112.json`

## Verification receipt

- Tier 0: changed Python and structured-data inputs parse; scoped
  `git diff --check` — PASS.
- Tier 1 producer:
  `python3 -m closed_universe_observers.generate_berger_apparatus_combined_q1_after_replacement_112 --write`
  — PASS.
- Tier 1 independent verifier:
  `python3 -m closed_universe_observers.verify_berger_apparatus_combined_q1_after_replacement_112`
  — PASS.
- Tier 1 tests:
  `python3 -m pytest -q closed_universe_observers/tests/test_berger_apparatus_combined_q1_after_replacement_112.py`
  — PASS, 5 tests (1.33 s).
- Tier 2 atlas generator and independent verifier — PASS.
- Tier 2 direct consumers — PASS, 60 tests (28.91 s).
- Paper 09 compiled twice with `pdflatex` into a temporary output directory —
  PASS (18 pages); no out-of-scope PDF was written to the worktree.
- Tier 3 is not run: this is a scoped unary pushout, not a programme freeze,
  shared-core change or release.
