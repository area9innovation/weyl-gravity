# Phase-2 compact-block CPT feasibility

Result: `STRUCTURED_ETA_CONE_CLASSIFIED_AND_UNIQUE_FUNDAMENTAL_SYMMETRY_CONSTRUCTED_PT_DATUM_ABSENT`.

## Commutant first

Use the positive-frequency branch frame with both axial and polar copies.
The exact squared frequencies are

```text
k^2+lambda-sqrt(2 lambda),
k^2+lambda+sqrt(2 lambda),
k^2+lambda-2/3  (multiplicity two).
```

They are pairwise distinct for `lambda=ell(ell+1)>=6`.  Solving the complete
matrix commutator before any metric equation gives

```text
Comm(H,H_product) = M_2(C) direct-sum M_2(C) direct-sum M_4(C)
```

of complex dimension 24.  The multiplicities are two on each Einstein shell
and four on the extra shell.  The connected orientation-preserving
`H_product` does not distinguish isospectral axial and polar copies.  If a
separate fixed-bundle discrete parity were supplied, its graded subcommutant
would be two copies of `C direct-sum C direct-sum M_2(C)`, of dimension 12;
that is only an optional algebraic slice here, not the full invariant answer.

Here the displayed diagonal operator is `H^2`, not `H`.  On the physical
domain all three entries are strictly positive: `lambda-sqrt(2lambda)>0`
because `lambda>=6>2`, and `lambda-2/3>=16/3`.  The positive-frequency
Hamiltonian is therefore the positive spectral square root

```text
H = diag(sqrt(q_minus),sqrt(q_plus),sqrt(p),sqrt(p)).
```

The square root is injective on this positive spectrum, so `H` and `H^2`
have identical spectral projectors and identical commutants.  Every classified
`eta` is block diagonal on those projectors, proving
`H^dagger eta=eta H`.  Likewise `C0` is a polynomial in `H^2` and commutes
with `H`.  The separately displayed relative spectral operator maps the
Einstein action form to the restricted Weyl action form; it is neither `H`
nor `H^2`.

## Complete structured metric cone

In this spectral frame every rational or polynomial full-`H_product`
compatible Hermitian metric is

```text
eta = A_minus direct-sum A_plus direct-sum A_p,
sizes = 2, 2, 4.
```

It is strictly positive exactly when all three Hermitian multiplicity matrices
are positive, equivalently when their exact LDL pivots (or leading principal
minors in the declared frame) are positive.  The previous scalar-plus-`2x2`
conditions describe only the optional parity-graded slice.

The coefficient functions must have no poles on the declared physical
parameter domain.  Real-field completion requires
`eta(lambda,-k)=conjugate(eta(lambda,k))`: entrywise real parts are even in
`k`, while entrywise imaginary parts are odd.  Thus all three
matrices are real symmetric at `k=0`.  Candidate-dependent singular walls are
poles, zero LDL pivots, or `det(A_minus)det(A_plus)det(A_p)=0`.

This is a nonempty cone, not a metric manufactured independently in each
eigenbasis.  A choice fitted separately for each eigenvector, `m`, or `k`
without the tensor transformation law, harmonic equivariance, reality
relation and a pole-free parameter family is rejected.

## Canonical positive fundamental symmetry

Let `G` be the imported action-derived positive-frequency Hermitian form.  Its
generic signature is `(3,1)`: the negative line is the Einstein `q_minus`
shell, while `q_plus` and the two extra directions are positive.  The
basis-free projector

```text
P_minus = ((H^2-q_plus I)(H^2-p I)) /
          ((q_minus-q_plus)(q_minus-p))
```

defines

```text
C0 = I-2 P_minus,       eta0 = G C0.
```

Exact matrices verify `C0^2=1`, `[C0,H]=0`, `C0^dagger G=G C0`, and
`eta0>0` for every physical `lambda>=6` and real `k`.  On the two-dimensional
extra block `C0=I`.

This candidate is unique within the declared commutant.  Positivity forces
`C=-I_2` on the full negative `q_minus` multiplicity and `C=+I_2` on
`q_plus`.  On the positive-definite four-dimensional extra block, any
`G`-self-adjoint involution with a `-1` eigenspace would make `GC` negative
there, so `C=I_4`.  This remains true with arbitrary axial/polar mixing.

The proof is basis invariant.  Under a branch-frame change `B`,

```text
H'=B^-1 H B,  G'=B^dagger G B,  eta'=B^dagger eta B,  C'=B^-1 C B.
```

All defining equations, commutant dimension, rank, inertia and strict
positivity are preserved.

## Walls and exceptional ledger

The intrinsic spectral collision walls are `lambda=0` and `lambda=2/9`.
The action forms additionally degenerate at the exact factors recorded in the
certificate, including `lambda=2`; the polar extra determinant also contains
`3k^2+3lambda-2` and `(6k^2+3lambda-2)^2`.  None meets the physical domain
`lambda>=6`.

No exceptional or residual sector is silently omitted:

- Standard radiative `ell=1` axial and polar lines are positive and admit all
  positive diagonal metrics; their unique positive `GC` involution is `I`.
- Exceptional `ell=1` extra lines are likewise positive at zero and nonzero
  momentum.  The imported compact Taub theorem nevertheless rejects every
  nonzero pure exceptional tangent at second order.
- Homogeneous and twist blocks are generalized-zero/Jordan carriers with zero
  relative solution cofiber and no imported positive-frequency complex
  structure, so this pilot marks them not applicable rather than assigning a
  metric.
- The imported residual result retains branchwise cohomology as an
  `H_product` representation, but supplies neither invariant-state cohomology
  nor a global orbit/symplectic quotient.  No residual-state positivity claim
  follows.

## Why this is not yet a Mannheim C operator

`C0` is an exact, unique fundamental symmetry candidate, but the imported
fixed-`N=2` carrier declares only the orientation-preserving connected group
and the real-field conjugation.  It does not provide an independent linear
`P`, anti-linear time reversal `T`, a `[C,PT]` test, or the convention relating
`eta`, `P`, and `C`.  In particular, an orientation-reversing parity may move
the magnetic bundle to another charge sector and cannot be invented as an
endomorphism of the fixed fibre.  Therefore no genuine Mannheim `C` is
claimed.  A typed discrete `P/T` or combined parity-charge-conjugation
crosswalk is the next required input.

## Evidence and boundary

The independent verifier recomputes the positive-frequency Hamiltonian
convention and commutant, the two exact `q`-block
fundamental symmetries, all determinant factorizations and the exceptional
and residual ledger.  It rejects eight decisive mutations.

This is `LOCAL-ALGEBRAIC` / `REDUCED-MODE`.  It establishes neither a genuine
Mannheim `C`, invariant-state metric, Hadamard state, particles, interacting
positivity, scattering, anomaly/QME restoration nor unitarity.

## Test tiers

- Tier 0: Python compilation, JSON/schema parsing, whitespace and scoped diff.
- Tier 1: producer replay, independent verifier, mutations and scoped tests.
- Tier 2: not run; all mathematical inputs are unchanged and hash-pinned.
- Tier 3: not run; no freeze, release or lifecycle promotion occurs.

CLOSE-OUT: DONE — the complete structured eta cone and its singular walls are classified, the unique positive fundamental symmetry is constructed basis-invariantly, and the first genuine-C obstruction is the absent certified P/T datum.
EVIDENCE: quantum-weyl/pt_cpt/compact_blocks/receipts/COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1_TIER_RECEIPT.json
