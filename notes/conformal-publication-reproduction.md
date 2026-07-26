# Paper 7 publication and reproduction guide

This guide is the public entry point for reproducing the free pure-Weyl
publication pair:

- Paper A: `paper/07-conformal-residual-cohomology-krein.tex`;
- Paper B: `paper/08-conformal-covariant-causal-transport.tex`.

The versioned supplement is
`paper/07-08-conformal-residual-cohomology-computational-supplement.tex`.  The
combined `paper/07-08-conformal-residual-cohomology-archive.tex` is archival: it preserves
the original equation labels and implementation chronology but is no longer
the primary submission.  Commands are run from
the standalone `weyl-gravity` repository root unless stated otherwise.

## Certified theorem

For the selected closed-cylinder BV--BFV polarization, the support-local
curvature prolongation and direct adjoint-tractor transfer give causal
homotopies on all 386 prolonged rows.  Their causal difference is a
compact-to-global quasi-isomorphism on `R x S3`.  Temporal-cutoff sources
recover the fifteen conformal-Killing ghosts and their fifteen dual endpoint
classes without duplication.  The residual `SO(4,2)` action transfers up to
an explicit compactly supported chain homotopy, and the direct cyclic
Green/current comparison transports the normalized pairing.  Therefore

```text
H4_cov = span{[W_+^2], [W_-^2]}
G_cov  = I2
```

This is a `LORENTZIAN-CAUSAL` free classical theorem.  The residual
Chevalley--Eilenberg calculation is transported; it is not recomputed in the
auxiliary or prolonged variables.

The generated
[covariant H4 proof ledger](../covariant_completion/generated/covariant_H4_proof_ledger.md)
binds every terminal claim to its authoritative evidence, canonical digest,
and exact reproduction command.

The referee major-revision architecture is documented in the
[Paper A/Paper B/supplement split roadmap](conformal-paper-split-roadmap.md).
The corresponding
[response ledger](conformal-referee-major-revision.md) separates completed
manuscript repairs from submission gates that still require a public artifact
release or independent expert review.
The split is implemented by the two standalone entrypoints above.  The
versioned computational supplement is tracked at
[`paper/07-08-conformal-residual-cohomology-computational-supplement.tex`](../paper/07-08-conformal-residual-cohomology-computational-supplement.tex).

## Scoped legacy and no-go routes

Two machine flags intentionally remain false:

```text
prolonged_green_witness           = false
curvature_causal_green_operators = false
```

They refer to the superseded canonical endpoint-inverse and monolithic
degreewise-witness implementations.  They are not dependencies of the direct
tractor causal route and are not active blockers.

The following negative results also remain part of the theorem record, with
their stated scope:

- the 24-field/9-gauge scalar-symbol normally-hyperbolic witness is excluded
  by the exact null-rank inequality `11 > 9`;
- the fixed-temporal pair-`1+6`, cyclic 46-parameter strongly-hyperbolic
  family has a parameter-rigid Jordan chain;
- the complete invariant direct two-wave factorization family is excluded by
  its exact polynomial certificate.

These statements do not refute the BV complex, its causal homotopy, or the
final covariant cohomology theorem.  Historical factorization, saddle, and
first-order searches in the READMEs are retained as design/no-go receipts,
not as the current completion path.

## Fast required rail

Use this for pull requests and ordinary commits.  It runs every non-slow
positive paper certificate and every fail-closed overclaim guard:

```bash
python3 -m pip install -r symbolic/conformal-paper-requirements.txt
python3 symbolic/verify_conformal_paper_free.py --required --timeout 180
python3 symbolic/verify_conformal_covariant_dependency_report.py
python3 symbolic/verify_conformal_final_covariant_transport.py
python3 symbolic/verify_conformal_four_flag_closure.py
python3 symbolic/verify_conformal_certificate_provenance.py
python3 symbolic/verify_conformal_covariant_H4_proof_ledger.py --check --guards
python3 symbolic/verify_conformal_residual_rank53_independent.py
python3 symbolic/verify_conformal_split_publications.py
python3 -m unittest covariant_completion.final_transport.tests.test_proof_ledger
python3 symbolic/update_conformal_paper_snapshot.py --check
```

The required CI job has a 20-minute job timeout and uploads its console log.
A timeout is a failure, never a theorem promotion.

## Exhaustive reproduction rail

Use this for publication snapshots, freezes, releases, or after changing a
shared mathematical input:

```bash
python3 symbolic/verify_conformal_paper_free.py --reproduce --timeout 1800
python3 symbolic/verify_conformal_covariant_completion.py --emit --guards
python3 symbolic/verify_conformal_certificate_provenance.py
python3 symbolic/verify_conformal_covariant_H4_proof_ledger.py --check --guards
python3 -m unittest covariant_completion.final_transport.tests.test_proof_ledger
git diff --exit-code -- analytic_completion covariant_completion
python3 symbolic/verify_programme_introduction.py --check-report --guards
sha256sum -c symbolic/programme-introduction-verification.sha256
python3 symbolic/update_conformal_paper_snapshot.py --check
```

The exhaustive CI job runs on the weekly schedule and manual dispatch, has a
four-hour job timeout, and uploads its log, generated certificates, generated
reports, dependency manifest, and paper PDF.  Exact duration is
machine-dependent; individual verifier subprocesses are bounded to 30
minutes.

For a release or referee artifact review, run the clean tracked-snapshot
audit as a separate gate:

```bash
python3 symbolic/audit_conformal_publication_release.py \
  --tree-ish HEAD \
  --timeout 1800 \
  --receipt conformal-publication-release-audit.json
```

This command uses `git archive`; it never builds from the dirty development
tree. It checks that Paper A, Paper B, the supplement, the archival monolith,
their PDFs, and all recursively active TeX inputs are tracked in the selected
tree. It then verifies generated-input freshness, builds all four documents
to reference stability, and runs the independent residual-rank, provenance,
proof-ledger, and manifest checks.

To rebuild the paper after the exact rail passes:

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error 07-conformal-residual-cohomology-krein.tex
pdflatex -interaction=nonstopmode -halt-on-error 07-conformal-residual-cohomology-krein.tex
pdflatex -interaction=nonstopmode -halt-on-error 08-conformal-covariant-causal-transport.tex
pdflatex -interaction=nonstopmode -halt-on-error 08-conformal-covariant-causal-transport.tex
pdflatex -interaction=nonstopmode -halt-on-error 07-08-conformal-residual-cohomology-archive.tex
pdflatex -interaction=nonstopmode -halt-on-error 07-08-conformal-residual-cohomology-archive.tex
pdflatex -interaction=nonstopmode -halt-on-error 07-08-conformal-residual-cohomology-computational-supplement.tex
pdflatex -interaction=nonstopmode -halt-on-error 07-08-conformal-residual-cohomology-computational-supplement.tex
cd ..
python3 symbolic/update_conformal_paper_snapshot.py --write
python3 symbolic/update_conformal_paper_snapshot.py --check
```

Commit the TeX, PDF, and refreshed manifest together for a publication
snapshot.

## Deliberately out of scope

The completed theorem does not claim a Hadamard state, distributional
completion, arbitrary-background causal theory, interacting or nonlinear
stability, quantum-master-equation restoration, anomaly cancellation,
positive graviton Hilbert space, integrated `SO(4,2)` group representation,
or uniqueness among boundary/deparametrized polarizations.  Those are future
work and must not be inferred from a passing classical free-theory rail.
