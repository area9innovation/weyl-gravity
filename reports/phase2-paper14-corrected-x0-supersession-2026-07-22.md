# Paper 14 corrected-X0 supersession

Result: `PAPER_14_CORRECTED_X0_SUPERSESSION_V1`

Lifecycle: `DRAFT_ALLOWED`

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

Paper 14 now imports the terminal generic-angular Schwarzschild disposition
from commit `936d76dbd2a9149243e57a082fa3519f0cfa8724` and no longer presents the
defective axial or shallow polar infinity fixtures as Einstein-only selection
theorems.

The corrected manuscript establishes, at the exact scope of the imported
formal calculations:

- the two axial Einstein densities fall as `r^-2` for every integer
  `ell>=2` and real nonzero frequency;
- the legacy axial `X0` metric lift omitted `2 r c'(r)/(r-2M)`, leaving the
  exact Ricci-row defect `c'(r) S_ell`, equal to `S_2/2+O(r^-2)` at the old
  fixture;
- the corrected axial `X0` lift is non-Einstein, extends to all formal radial
  orders modulo the declared Einstein shift, and has finite radial Lee--Wald
  pairing on the whole declared domain;
- the restriction-stable polar module has a one-dimensional mixed
  Einstein/additional line that is finite through the nonintegrable layers
  and generically nonradical;
- the first finite polar coefficient has exact exceptional wall
  `Q21(ell(ell+1),omega^2)=0`, with exact real-root counts by harmonic;
- at the legacy point `Lambda=6`, `(M omega)^2=9/25`, the corrected `Q21`
  value is exactly nonzero.  The previously recorded longer rational was the
  double-squared evaluation at `81/625`, not a norm.

The static Laurent classification, normalized static first law, Ricci-to-Bach
composition, axial and polar future-horizon reach, exact Einstein isotropy,
controlled horizon pairings, endpoint regularity/leading-symbol
nonselection, local Cauchy selection and horizon monodromy theorem are
preserved.

## Superseded claims

The following are no longer active Paper 14 claims:

- axial or parity-complete Einstein-only finite radial selection;
- the legacy axial `X0` logarithmic tail and divergent-current table;
- the shallow polar power-enhanced/logarithmic lift and divergent composed
  table;
- a representative-invariant Einstein/extra signature inferred from those
  infinity fixtures;
- the infinity-selection half of the endpoint assembly;
- the additional-log-tail half of the exterior boundary-value disposition.

The append-only coverage overlay marks the two former Paper 14 result edges
as stale by supersession and adds the terminal generic-angular result as the
new primary theorem-correction edge.  The Phase-1 coverage overlay is not
rewritten.

## Claim boundary

The corrected result is a formal infinity-mode classification in a fixed
Lee--Wald representative.  It does not establish convergence or summability,
axial `X2`, extension of terminal-only polar prefixes, the deeper filtration
on the `Q21` wall, horizon-to-infinity matching, a differentiable
asymptotically flat phase space, a Hilbert norm, scattering, quasinormal
modes, stability, particles, positivity or any quantum theorem.

In particular, the paper now distinguishes three statements:

1. future-horizon and leading-symbol tests do not force the Ricci carrier to
   vanish;
2. local zero Ricci-carrier Cauchy data do select the Einstein kernel at the
   linear level;
3. formal radial pairing finiteness does not select the Einstein image, while
   the existence of one global solution satisfying both endpoint conditions
   remains open.

## Reproducibility

The deterministic generator pins 26 committed active inputs.  The independent
verifier replays the terminal hashes, source blobs, Q21 root-count ledger and
legacy fixture; checks preserved and superseded scope flags; scans the
manuscript for required and forbidden claims; and verifies the append-only
coverage correction.  Five tests include adversarial mutations of the
selection flag, the Q21 substitution, the old selection sentence and a global
matching promotion.

Commands:

- `python3 paper/generate_14_pure_weyl_black_hole_radiation_claim_map.py --check`
- `python3 paper/verify_14_pure_weyl_black_hole_radiation_claim_map.py`
- `python3 -m unittest paper/test_14_pure_weyl_black_hole_radiation_claim_map.py -v`
- `python3 paper/verify_13_14_draft_source_maps.py`
- two final `pdflatex -interaction=nonstopmode -halt-on-error` passes from a
  stable isolated auxiliary directory; both final logs contain no LaTeX,
  package, box, reference or rerun warnings.

Tier 0 and scoped Tier 1 pass.  The affected publication/source-map chain is
replayed.  The heavy radial/current producers are not rerun because the
publication correction imports their committed content-addressed terminal
certificates.  Repository-wide Tier 3 is not required for a draft-paper
correction; the dedicated mutation rail and shared Paper 13/14 source-map
audit are the affected chain.

CLOSE-OUT: DONE — Paper 14 now reports the corrected generic-angular axial
counterexample and polar Q21 finite-line disposition, preserves independent
static/horizon/local-Cauchy results, and append-only supersedes every active
Einstein-only infinity-selection edge that relied on the defective legacy
lift.

EVIDENCE: `reports/PAPER14_CORRECTED_X0_SUPERSESSION_TIER_RECEIPT.json`
