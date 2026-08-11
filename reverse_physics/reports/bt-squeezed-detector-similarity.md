# BT squeezed-detector similarity

**Result:** `COEFFICIENT_COMPUTED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The covariant Appendix-C squeeze cannot restore the logarithmic coefficient
that cancels in the complete signed quadratic map.  On every certified finite
paired core it is a cross-Krein similarity of the entire observable, not an
independent additive projector contribution.

## Exact operator statement

Factor the public finite-regulator map as

\[
 R(\lambda)=S U(\lambda),\qquad U(\lambda)=1+\lambda K+O(\lambda^2).
\]

On the paired core, \(S^\dagger=S^{-1}\).  Therefore

\[
 K_S=SKS^{-1},
 \qquad
 K_S^\dagger K_S=S(K^\dagger K)S^{-1}.
\]

The detector projector is transported by the same similarity:

\[
 RPR^\dagger=S(UPU^\dagger)S^{-1}.
\]

For finite-rank paired-core operators, cyclicity gives

\[
 \operatorname{Tr}_{\rm fin}(STS^{-1})
 =\operatorname{Tr}_{\rm fin}(T).
\]

Thus the complete signed kernel's zero parent-raised quadratic trace remains
zero after the squeeze.  Eight exact sign/energy fixtures independently
transport the kernel through parent and daughter Krein isometries and obtain
zero before and after.  A three-dimensional exact rational projector fixture
also preserves idempotence, unit trace, and the zero trace of its
order-\(\lambda\) commutator coefficient.

## Why bare pair occupation is different

For one normalized squeezed pair,

\[
 |\widehat\Psi_z\rangle
 =\sqrt{1-x}\sum_{n\ge0}z^n|n,n\rangle,
 \qquad x=|z|^2.
\]

A *bare* one-pair Fock projector has probability

\[
 (1-x)x.
\]

At \(z=1/2\), this is \(3/16\).  It is not an additional interaction
coefficient.  It keeps the \(b\)-Fock detector fixed while changing the
vacuum, whereas Eq. (19) pushes the detector through the same map.  Adding the
bare occupation to the covariant coefficient would compare two different
observables and double-count the squeeze.

## Disposition

Established exactly:

- the squeeze-similarity identity for the quadratic Born operator;
- preservation of the complete signed-kernel zero on finite paired cores;
- preservation of finite-rank projector idempotence and cyclic trace;
- zero additive squeeze correction;
- the distinction between bare pair occupation and covariant detector
  transport.

The complete public finite-regulator order-\(\lambda\) quadratic coefficient
is therefore zero.  This is not a physical-zero theorem.  The positive trace
norm of the squeezed projector grows exponentially with volume, so the
finite-rank cyclic identity has no certified thermodynamic \(L^1\) limit.  A
local non-normal weight, the full dynamical \(p=0\) module, and higher
composite orders remain missing.  Nothing here is gravitational, BRST, or
`LORENTZIAN-CAUSAL`.

## Verification receipt

All commands ran sequentially under the 500,000 KB virtual-memory cap.

- Python parse/compile: PASS in 0.03 s, 16,156 KB peak RSS.
- Work item, event, schema, and certificate JSON parse: PASS in 0.14 s,
  14,752 KB peak RSS.
- Scoped `git diff --check`: PASS in 0.00 s, 10,780 KB peak RSS.  The
  following default status/stat calls could not create Git's threaded index
  scan because the host temporarily lacked a thread resource; they are not
  counted as passes.  Deterministic retries with `core.preloadIndex=false`
  passed and showed only the scoped files.
- Certificate generation: PASS in 0.04 s, 20,904 KB peak RSS.
- Producer: `python3 reverse_physics/bt_squeezed_detector_similarity.py
  --check` — 20/20 checks in 0.04 s, 20,564 KB peak RSS.
- Independent verifier:
  `python3 reverse_physics/verify_bt_squeezed_detector_similarity.py` —
  10/10 checks in 0.11 s, 30,112 KB peak RSS.
- Mutation suite: `python3 -m unittest -v
  reverse_physics.tests.test_bt_squeezed_detector_similarity` — 7/7 tests
  in 0.77 s, 30,492 KB peak RSS.  Mutations changed the transported trace,
  projector, bare occupation, continuum lifecycle, and physical-zero boundary;
  every mutation was rejected.
- Papers V and VI compiled twice with `pdflatex -interaction=nonstopmode
  -halt-on-error`.  Paper V took 0.42/0.43 s and at most 50,852 KB peak RSS;
  Paper VI took 0.45/0.45 s and at most 50,728 KB.  The final PDFs have 29
  and 37 pages, with no undefined reference or fatal LaTeX error.

Tier 2 stops at the directly consuming papers because all predecessor
certificates are unchanged and content-addressed.  Tier 3 is not required:
the certificate computes a finite-regulator coefficient and explicitly does
not promote a continuum, all-order, freeze, or physical theorem.  The Science
Forge transition is an append-only manual `event-v0` fallback with an
independently reproduced FNV-1a id; no coordinator pass is claimed.
