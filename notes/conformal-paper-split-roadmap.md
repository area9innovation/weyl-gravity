# Paper 7 major-revision split roadmap

This is an editorial plan, not a new theorem or a change to the certified
dependency graph.  The current monolithic source
`paper/conformal-residual-cohomology.tex` remains the buildable archival
version until both extracted papers and the computational supplement pass
their own reference, bibliography, and certificate checks.

## Publication units

### Paper A — residual cohomology and pairing

Provisional title: **Residual cohomology of free pure-Weyl gravity on the
conformal cylinder**.

Its mathematical spine should be:

1. the free local detour complex and the global deformation-complex theorem;
2. the on-shell Weyl module, its `E/A/L` character, and invariant Krein form;
3. the conformal moment-map/Taub normalization;
4. Cartan reduction to the finite centered inventory;
5. the exact absolute residual calculation
   `H4_res = span{[W_+^2],[W_-^2]}` with Gram matrix `I2`;
6. descent to the parity basis and the dynamical/topological quotient;
7. only the algebraic portion of the local-to-residual transfer needed to
   state precisely which residual BV--BFV polarization is being computed.

The current sections `The on-shell Weyl module` through `Descent and the
dynamical/topological split` form the core.  The finite-jet convention audit,
large basis dictionaries, gauge-fixed row ledgers, and measured-cutoff
implementation details should be cited from the supplement rather than
repeated in the article.

Claim boundary: Paper A proves the residual theorem in the selected
polarization.  It does not use the residual calculation as evidence for a
Lorentzian causal BV theorem.

### Paper B — covariant causal bridge

Provisional title: **Causal curvature prolongation and covariant transport
for the free pure-Weyl BV complex**.

Its mathematical spine should be:

1. the curved auxiliary Hessian, support-local BV-canonical retract, and
   off-shell current comparison;
2. the scoped `11 > 9` scalar-wave witness no-go and the physical
   helicity-two Weyl-symbol quotient;
3. the exact Weyl--Cotton first-order closure, symmetric-hyperbolic
   constraint adjustment, and sourced subsidiary system;
4. the all-row curvature mapping cylinder and cyclic `356+30` retract;
5. the adjoint-tractor parent Green homotopy, trace/Weyl shear, and resulting
   all-row retarded/advanced homotopies;
6. the compact-to-global causal quasi-isomorphism, endpoint recovery,
   homotopy-equivariant `SO(4,2)` transport, and current/Green pairing;
7. transport of Paper A's already-computed residual theorem to
   `H4_cov = span{[W_+^2],[W_-^2]}`, `G_cov = I2`.

The curved part of `The free local pure-Weyl complex` and the theorem
`Covariant causal transport` form the core.  Paper B should quote Paper A's
residual theorem rather than reproduce the centered CE matrices.

Claim boundary: the direct tractor homotopy is the completed causal route.
The canonical endpoint same-sided inverse and monolithic prolonged witness
remain scoped legacy implementation flags and are not premises of Paper B.

### Computational supplement

The supplement should be a repository-linked, versioned companion shared by
Papers A and B.  It should contain:

- convention tables and finite-jet globalization audits;
- sparse-matrix formats, good-prime rank witnesses, and exact null vectors;
- the raw/minimal/gauge-fixed basis dictionaries and all-row ledgers;
- the detailed curvature row layouts, PBW normal forms, and mapping-cylinder
  coefficient tables;
- scoped unsuccessful factorization and first-order searches, including the
  exact no-go receipts;
- the endpoint Nullstellensatz identity;
- certificate schemas, SHA-256 provenance, verifier commands, elapsed-time
  classes, and the terminal proof ledger;
- independent cross-checks which do not import the authoritative
  implementation.

The long implementation chronology currently embedded in the curved
subsection and in `Raw polynomial instantiation and measured noncompact
defects` is supplement material.  It remains in the archival monolith during
the split so equation labels and cross-references do not silently change.

## Safe extraction sequence

1. Freeze the current monolith, PDF, dependency manifest, and proof ledger.
2. Create Paper A by copying theorem prose, not by moving source in place.
   Replace implementation-ledger paragraphs with stable supplement
   references only after the copied paper builds independently.
3. Create Paper B in the same way and import Paper A's residual theorem as an
   explicit dependency.
4. Extract the marked implementation-history blocks into a standalone
   supplement.  Preserve their original equation labels with a prefix or a
   label map so old certificate reports remain interpretable.
5. Add per-publication verification runners and manifests.  Only then remove
   duplicated implementation material from the article sources.
6. Keep the archival monolith in the repository until both articles and the
   supplement reproduce from a clean checkout.

This copy-first sequence avoids breaking the current paper while the split is
under referee review.

## Current source-to-destination map

| Current material | Destination | Editorial action |
|---|---|---|
| Introduction and claim boundary | A and B | Rewrite separately around each theorem |
| Local detour/BGG complex | A; summarized in B | Keep theorem, move coordinate audit to supplement |
| Curved auxiliary and Weyl-curvature route | B | Keep theorem chain; move search chronology and coefficient ledgers to supplement |
| Weyl module and moment map | A | Keep |
| Cartan reduction and centered cohomology | A | Keep |
| Descent and dynamical/topological split | A | Keep |
| Raw polynomial instantiation and cutoff defect measurements | Supplement | Retain only the resulting proposition and dependency boundary in A |
| Dual endpoint/BFV shift and selected polarization | A; summarized in B | Keep conceptual theorem, move record-by-record ledgers to supplement |
| Causal quasi-isomorphism and pairing transport | B | Keep |
| Exact-rank and Nullstellensatz appendices | Supplement | Replace in articles by receipt references |
| Claim-status and verification index | Supplement | Give each article a short theorem-dependency table |

## Generated-input audit

The current paper has exactly one generated TeX input:

```text
paper/generated/endpoint_factorization_nullstellensatz.tex
```

It is tracked by Git, names its generator and source-certificate digest in
its header, and is included only by the endpoint no-go appendix.  The other
tracked generated TeX fragments are standalone receipts rather than active
`\input` dependencies:

```text
analytic_completion/generated/completed_residual.tex
analytic_completion/generated/energy_mode_krein.tex
covariant_completion/generated/auxiliary_green_witness.tex
covariant_completion/generated/cauchy_sobolev.tex
covariant_completion/generated/covariant_bv_last_mile_status.tex
covariant_completion/generated/curl_factorization.tex
covariant_completion/generated/minimal_ghost_witness.tex
```

The supplement must distinguish active TeX inputs from historical generated
receipts.  In particular, `covariant_bv_last_mile_status.tex` records a
superseded canonical-witness checkpoint and must not be presented as the
current direct-tractor dependency status.

## Independent residual-rank cross-check

The small standalone checker

```bash
python3 symbolic/verify_conformal_residual_rank53_independent.py
```

uses only the Python standard library.  It independently constructs the
integral spin-two action on
`Sym^2((2,0) + (0,2))`, obtains the block decomposition
`55 = 15 + 25 + 15`, proves modular ranks `53 = 14 + 25 + 14` at two primes,
and exhibits two exact independent chiral singlets.  The modular lower bound
and exact two-dimensional kernel give the characteristic-zero rank `53`.

This checks the central lowest-two-particle rank without importing the
project's conformal-generator, Fock, or BRST code.  It does not replace the
authoritative one-particle absolute window, CE nilpotency, BV--BFV transfer,
or pairing certificates.

## Acceptance gates for the split

Each article and the supplement should have:

- a standalone two-pass TeX build with no undefined references;
- a short claim ledger containing only claims used by that publication;
- an exact dependency manifest and clean-check command;
- at least one independent checker for its central finite computation;
- fail-closed guards for the adjacent claims it does not prove;
- an explicit dependency tag (`LOCAL-ALGEBRAIC`, `REDUCED-MODE`, or
  `LORENTZIAN-CAUSAL`) on every headline result.

Until those gates exist, the current monolith remains the authoritative
publication artifact.
