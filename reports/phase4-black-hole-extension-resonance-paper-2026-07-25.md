# Paper 17: non-split extension and defective resonance

Date: 2026-07-25

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

Paper 17 has been promoted from a three-page companion scaffold to a
fourteen-page theorem-first draft titled:

> A Non-Split Regge--Wheeler Self-Extension and a Defective Schwarzschild
> Resonance in Pure Weyl Gravity

The draft now proves and organizes four linked results:

1. the exact axial RW/RW/Maxwell filtration, partial-jet realization, and
   physical-axis non-splitting of the repeated spin-two block;
2. the projective normal form
   \[
   [\mathcal I_{\rm Bach}]
   =\frac{i\omega}{2}\left[1-\frac2r\right];
   \]
3. the resonant-evaluation identity
   \[
   \kappa_n
   =\frac{b(\omega_n)}{a'(\omega_n)}
   =\frac{\beta_n}{\alpha_n}
   =-\omega_n'(0);
   \]
4. a non-Einstein generalized root vector and a nonzero rank-one
   second-order pole of the compact-source, locally observed reduced radial
   Green operator.

The generalized carrier coefficient and invariant pole residue are now
written as
\[
(c_1)_Y=-\frac1{\kappa_n},
\qquad
R_{-2}=-\frac{\kappa_n}{\alpha_n}
u_n\otimes\widetilde u_n.
\]

The resonant overlap
\[
\mathfrak M_n([K])
=\langle\widetilde u_n,Ku_n\rangle
\]
is proved to descend to the extension class. This separates global
non-splitting from mode-specific defectiveness: a nonzero extension class
can evaluate to zero at an isolated resonance.

## Exact additions

- The triangular gauge is specified as
  \[
  Q(q)=qD-\frac12D(q),
  \qquad
  [L,Q(q)]|_{\ker L}=-\frac12\mathcal K_U(q).
  \]
- The symmetric-square period matrix is derived explicitly.
- The fixed-minor nonsplitting witness and dual-number commutant proof are
  included in the paper.
- The finite-interval outgoing Green pole is proved with an explicit cutoff
  Jost source showing that its principal covector is nonzero.
- The exact parent/radial comparison target is stated as
  \[
  K_{\rm radial}-P\mathcal A R=LQ-QL
  \]
  in the augmented boundary pencil.

## Claim boundary

The draft does not promote:

- the mass-shaped cocycle representative to a physical Einstein--Weyl mass
  parameter;
- the finite-interval radial pole to a causal spacetime resolvent;
- the double pole to a retarded \(t e^{i\omega_nt}\) term;
- axial \(\ell=2\) non-splitting to all harmonics;
- the spin-two commutant theorem to the complete six-state module;
- any stability, particle, ghost, or quantum-unitarity claim.

## Reproducibility

The new Paper 17 claim map pins nine existing exact or validated
authorities. Its verifier independently checks:

- the Bach cocycle normal-form identity in exact SymPy arithmetic;
- the triangular-gauge commutator;
- the symmetric-square period matrix;
- the root-chain sign and invariant resonance chain;
- all required upstream certificate flags and fail-closed boundaries.

Ten regression and mutation tests pass. Mutations of the cocycle, period
matrix, generalized-root sign, resonant-velocity sign, physical mass
promotion, causal resolvent promotion, ringdown promotion, and all-harmonic
promotion are rejected.

## Verification

Commands:

```text
python3 -m unittest paper/test_17_pure_weyl_extension_claim_map.py
python3 paper/generate_17_pure_weyl_extension_claim_map.py --check
python3 paper/verify_17_pure_weyl_extension_claim_map.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error \
  17-pure-weyl-schwarzschild-extension-structure.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  17-pure-weyl-schwarzschild-extension-structure.tex
git diff --check -- <scoped paths>
```

Outcome:

- 10 tests passed;
- generator drift check passed;
- semantic, symbolic, and provenance verifier passed;
- PDF compiled in two passes, 14 pages;
- scoped `git diff --check` passed.

Tier 2 was not rerun because no upstream mathematical input, operator,
certificate, or schema changed. Tier 3 was not run because this is a paper
promotion using unchanged content-addressed authorities, not a programme
freeze or release.

CLOSE-OUT: DONE — Paper 17 promoted with pinned claim map, exact verifier,
mutation tests, compiled PDF, and fail-closed resonance scope.
EVIDENCE: reports/PAPER17_EXTENSION_RESONANCE_TIER_RECEIPT.json
