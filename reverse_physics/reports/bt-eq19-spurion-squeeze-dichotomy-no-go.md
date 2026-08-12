# Full-map Bateman--Turok Eq. (19) charge--squeeze dichotomy

Certificate:
`REVERSE_PHYSICS_BT_EQ19_SPURION_SQUEEZE_DICHOTOMY_NO_GO_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Lifecycle: `CLASSIFIED`.

## Result

No homogeneous assignment of charge to the Bateman--Turok vacuum-orbit
factor makes the complete public finite-regulator map satisfy the two
necessary ingredients of Eq. (19): absence of positive-charge operators and
ghost evenness of the neutral term.

The conclusion includes both standard choices.  The fixed-vacuum oscillator
grading fails because the nonlinear map produces a positive-charge component.
The covariant zero-mode grading removes that positive charge, but makes the
Appendix-C squeeze neutral; the resulting neutral one-particle projector is
not ghost even.  Intermediate homogeneous assignments fail one of the same
two ways.

This is a finite-regulator theorem about the public regular architecture.  It
does not exclude a nonhomogeneous or enlarged charge algebra, a singular or
unbounded correspondence, an inequivalent non-Fock representation, or a
construction in which the finite witness is absent.

## The full map

The earlier nonlinear calculation must be placed inside the public
factorization

\[
 R(\lambda)=S\,U(\lambda),\qquad
 U(\lambda)=1+\lambda Z^{-1}K_++O(\lambda^2).
\]

Here \(S=\exp Q_S\) is the Appendix-C squeeze.  Its covariantly completed
creation monomial is

\[
 Z^2 b_\Upsilon^\dagger(\mathbf p)
     b_\Upsilon^\dagger(-\mathbf p),
\]

together with its Krein-adjoint annihilation term.  Assign

\[
 q(\Omega)=1,\qquad q(\Upsilon)=-1,\qquad q(Z)=s.
\]

The complete nonlinear tangent and the squeeze then have charges

\[
 q_K=1-s,
 \qquad
 q_S=2s-2=-2q_K.
\]

The locking relation \(q_S=-2q_K\) is the decisive fact: the two public
factors cannot both be moved strictly to the nonpositive side unless both
are neutral.

## Exhaustion of the charge assignments

For \(s<1\), \(q_K>0\) and \(q_S=-2q_K<0\).  Tensor the complete rank-four
nonlinear tangent with the squeezed-pair projector.  Its three displayed
charge components are

\[
 q_K,\qquad -q_K,\qquad -3q_K,
\]

of ranks \((4,8,4)\).  The first is the unique highest-charge component and is
nonzero.  Squeeze conjugation therefore cannot remove it.  In particular,
the fixed-vacuum choice \(s=0\) violates the public assertion that \(R_t\)
yields no positive-charge operators.

For \(s>1\), \(q_S>0\).  Before the nonlinear correction is applied, the
squeezed projector already has components of charges

\[
 0,\qquad q_S,\qquad 2q_S
\]

and ranks \((2,4,2)\) after tensoring with the two-species one-particle
projector.  Thus this half-line also violates the no-positive-charge premise.

The only remaining value is \(s=1\).  Both \(q_K\) and \(q_S\) vanish, so the
whole pushed projector is neutral.  Directness of the charge grading forces
the strictly negative Eq. (19) remainder to be zero.  The claimed ghost-even
neutral term must therefore be the complete projector.  The following exact
witness shows that it is not.

## Exact squeezed one-particle witness

Use one unordered nonzero momentum pair with basis

\[
 (|0\rangle,|\Omega\Omega\rangle,|\Upsilon\Upsilon\rangle)
\]

and pair Gram and ghost parity

\[
 J=\kappa=
 \begin{pmatrix}
 1&0&0\\0&0&1\\0&1&0
 \end{pmatrix}.
\]

At \(t=0\), write the real nonzero normalized pair amplitude as \(z\).  The
one-pair Appendix-C generator is

\[
 Q=
 \begin{pmatrix}
 0&-z&0\\0&0&0\\z&0&0
 \end{pmatrix},
 \qquad Q^\sharp=-Q,
 \qquad Q^3=0.
\]

Consequently its exponential is exact after the quadratic term.  Transporting
the pair vacuum \(P=\operatorname{diag}(1,0,0)\) gives

\[
 SPS^{-1}=
 \begin{pmatrix}
 1&zZ^2&0\\
 0&0&0\\
 zZ^2&z^2Z^4&0
 \end{pmatrix}.
\]

This is an idempotent Krein-self-adjoint projector of trace one.  Ghost parity
inverts the Laurent power and exchanges the two pair species.  Its canonical
odd part has nonzero supports \((Z^{-4},Z^{-2},Z^2,Z^4)\), with ranks
\((1,2,2,1)\), and

\[
 \tau_0(C^\sharp C)
 =-\frac{z^2(z^2+2)}2,
 \qquad
 \tau_0(B^\sharp C)=0.
\]

The defect is therefore orthogonal to the even part but is not null for any
real \(z\ne0\).

To put the witness in the stated \(n=1\) scope, tensor this pair with the
public two-species one-particle projector on a disjoint momentum fibre.  The
input before squeezing has exactly one particle and is ghost even.  The full
transported projector has trace two; its odd-support ranks become
\((2,4,4,2)\), and

\[
 \tau_0(C_{n=1}^\sharp C_{n=1})
 =-z^2(z^2+2).
\]

The normalized Appendix-C finite-box fixture has \(z=1/4\), giving the exact
nonzero value

\[
 -\frac{33}{256}.
\]

This failure occurs at order \(\lambda^0\) in the complete factorization and
cannot be repaired by higher nonlinear orders.

## Relation to the unsqueezed theorem

Certificate `REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1` exactly
computed the complete unsqueezed \(U(\lambda)\) tangent, including its rank
four and Laurent parity defect.  Those calculations remain valid for that
factor.  They are not, by themselves, the coefficient of the complete
squeezed projector because \(R=S U\).

The present theorem does not use that identification.  It uses the
unsqueezed tangent only where it is valid--as the unique positive component
for \(s<1\)--and treats \(SPS^{-1}\) exactly.  At the covariant value \(s=1\),
the full-map contradiction is already present in the squeezed free
projector.  The predecessor is therefore retained as an unsqueezed-factor
witness and superseded as the proof route for the full map.

## Exact boundary

Established:

- the charge-locking identity \(q_S=-2q_K\);
- exhaustive failure for every real homogeneous \(s\);
- positive charge at order \(\lambda\) for the fixed-vacuum grading;
- positive free squeeze charge for \(s>1\);
- an exact neutral, non-ghost-even \(n=1\) projector for \(s=1\);
- the non-null odd norm \(-z^2(z^2+2)\); and
- a full-map proof that does not treat the unsqueezed tangent as the complete
  coefficient.

Not established:

- a universal refutation of Eq. (19) in every representation;
- a no-go for nonhomogeneous, localized, doubled or enlarged charge data;
- a no-go for singular, unbounded, rigged or inequivalent non-Fock maps;
- a continuum, thermodynamic or asymptotic theorem;
- a generalized-Born trace or complete all-order probability;
- a Weyl-gravity, BV--BRST, QME or `LORENTZIAN-CAUSAL` result; or
- literature priority.

The separately certified selected tagged probability through
\(\lambda^6\) is unchanged and is not evidence for Eq. (19).

## Verification receipt

The exact producer passed `42/42` internal checks and the independent verifier
passed `45/45` checks using rational polynomial-list arithmetic rather than
SymPy or producer imports.  Nineteen tests, including seventeen adversarial
certificate mutations, passed.  All scientific processes were run
sequentially under `ulimit -v 500000`.

The producer completed in 0.40 s with maximum resident set size 69,264 kB; the
independent verifier completed in 0.36 s with maximum resident set size 26,328
kB; and the focused test file completed in 3.51 s with maximum resident set
size 68,988 kB.  Python compilation, JSON parsing, schema validation and the
scoped `git diff --check` rail passed.  The predecessor mathematical inputs
were unchanged and content-addressed, so Tier 2 used their hashes and the
independent verifier's import checks rather than rebuilding those certificate
chains.

Both papers compiled twice under the same memory cap.  Paper 05 finished its
second pass in 0.49 s with maximum resident set size 50,588 kB (59 pages,
655,924 bytes), and paper 06 in 0.50 s with maximum resident set size 50,528
kB (55 pages, 641,094 bytes).  No new overfull boxes were introduced.

Tier 3 was run and is **not** recorded as a pass: repository discovery ran
2,216 tests in 779.169 s (780.21 s wall time, maximum resident set size 391,500
kB), with 32 failures and 9 skips.  The new producer, verifier and all 19 new
tests passed inside that run.  The failures were confined to unchanged older
BT provenance/hash/executable rails and the existing `chain_imports` scan;
none was in this certificate package.  This failed repository-wide rail
precludes a freeze or release promotion but does not turn the passing scoped
certificate into a repository-wide pass.

The advisory Science Forge planning import is also **not** a pass.  It exited
2 immediately (0.00 s, maximum resident set size 3,672 kB) because the Go
runtime could not reserve page-summary memory within the 500 MB cap.  It was
not retried above the cap after the earlier out-of-memory incident.  A
skipped, capped or failed higher tier is never counted as a pass.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_eq19_spurion_squeeze_dichotomy_no_go.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_eq19_spurion_squeeze_dichotomy_no_go.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_eq19_spurion_squeeze_dichotomy_no_go
ulimit -v 500000; python3 -m unittest discover -v
ulimit -v 500000; pdflatex -interaction=nonstopmode -halt-on-error 05-interaction-obstructions.tex
ulimit -v 500000; pdflatex -interaction=nonstopmode -halt-on-error 06-einstein-weyl-interaction-obstructions.tex
```
