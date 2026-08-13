# BT kappa-fixed Born descent

**Certificate:** `REVERSE_PHYSICS_BT_KAPPA_FIXED_BORN_DESCENT_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

## Result

The local auxiliary pointer process has the same probability operator in the
public generalized Krein Born prescription and in the positive Hilbert Born
prescription.  This is an operator identity for the selected process, not an
assumption about a fitted coefficient:

\[
 A_g^\sharp A_g=A_g^*A_g=\sin^2(g|K|),
 \qquad A_g=P_{\rm click}U_gP_g .
\]

Consequently the certified response

\[
 {Q_{8,{\rm aux},{\rm compact}}\over\bar q_4}
 >{1\over18874368000}
\]

is a strictly positive selected public-BT auxiliary physical coefficient in
both prescriptions.

The same calculation gives a no-go theorem for the proposed general escape.
The canonical conditional expectation onto the ghost-even algebra cannot
remove a nonzero odd remainder without changing its public probability.

## Exact expectation theorem

Let \(\kappa\) be the positive carrier's fundamental symmetry and define

\[
 \alpha(A)=\kappa A\kappa,\qquad
 A_+=\frac{A+\alpha(A)}2,\qquad
 A_-=\frac{A-\alpha(A)}2.
\]

The positive and Krein adjoints satisfy

\[
 A^*=\kappa A^\sharp\kappa,
 \qquad A^\sharp=\kappa A^*\kappa .
\]

Trace invariance under \(\alpha\) makes the even and odd pieces
Hilbert--Schmidt orthogonal.  Therefore

\[
 \boxed{
 q_K(A):=\operatorname{Tr}(A^\sharp A)
 =\|A_+\|_2^2-\|A_-\|_2^2 .
 }
\]

The group average

\[
 E_\kappa(A)=\frac{A+\kappa A\kappa}{2}=A_+
\]

is the canonical normal, unital, completely positive, trace-preserving
conditional expectation onto the fixed-point algebra.  Its exact effect on
the public quadratic functional is

\[
 \boxed{
 q_K(E_\kappa A)-q_K(A)=\|A_-\|_2^2 .
 }
\]

On the faithful finite or Hilbert--Schmidt trace ideal, it preserves the
public weight if and only if \(A_-=0\), equivalently
\(\kappa A\kappa=A\).  Thus averaging is not a mechanism that turns a
nonfixed process into an equivalent physical one.  It is probability
preserving precisely when there was nothing to remove.

The certificate checks a nonsymmetric rational witness:

\[
 \kappa=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
 A=\begin{pmatrix}1&2\\3&4\end{pmatrix}.
\]

Its even and odd Hilbert squares are \(25\) and \(5\).  The public weight is
\(20\), whereas the expected operator has weight \(25\).  The defect is
exactly \(5\), the positive norm square of the discarded odd part.

This also explains the earlier weak-ghost witness.  For \(B=I\) and
\(Q=E_{21}\), the public generalized weight is two while the ordinary
Hilbert weight is three.  A conditional expectation does not make that
difference disappear.

## Why the pointer process passes

The complete pointer symmetry is stronger than weak ghost symmetry.  The
preceding local-unitary theorem proves

\[
 \kappa_{\rm tot}V\kappa_{\rm tot}=V.
\]

Bounded functional calculus gives the same identity for
\(U_g=e^{-igV}\).  The ground pointer projection is fixed, and ghost parity
exchanges the two click states while preserving their sum.  Hence

\[
 \kappa_{\rm tot}P_g\kappa_{\rm tot}=P_g,
 \qquad
 \kappa_{\rm tot}P_{\rm click}\kappa_{\rm tot}=P_{\rm click}.
\]

It follows that

\[
 \alpha(A_g)=A_g,
 \qquad A_g=P_{\rm click}U_gP_g.
\]

For a fixed operator the two adjoints agree:

\[
 A_g^\sharp=\kappa A_g^*\kappa=A_g^*.
\]

The public and positive effects are therefore the same bounded local
operator.  This identity holds for every real detector strength \(g\) and
every trace-class selected ground-sector input.  The finite selected pair map
independently verifies the same symmetry as
\(M\kappa_{\rm in}=\kappa_{\rm out}M\).

## What this means

The positive auxiliary detector is no longer merely a different Hilbert-space
reinterpretation of a public BT number.  For this complete selected local
process, both operational prescriptions give the same click effect and the
same strictly positive \(q_8\) tangent.  That is a genuine scoped physical
result inside the public auxiliary theory.

It is not general Eq. (19).  The theorem instead supplies a necessary and
sufficient test for every proposed extension: construct the complete
transition operator \(A\) and check \(\kappa A\kappa=A\).  If the test fails,
the canonical expectation changes the public probability by the exact
positive amount \(\|A_-\|_2^2\).  If it passes, the two Born rules agree on
that process without a quotient.

## Claim boundary

This result does not establish:

- equality of the two Born rules for arbitrary public processes;
- probability-preserving removal of a nonzero nonfixed remainder;
- total-kappa fixedness of every physical BT transition;
- the scalar projector pushforward or general Eq. (19);
- an interacting BT local net or time-ordered detector evolution;
- control of \(\lambda^{10}\) and higher response terms;
- a thermodynamic normal trace on the identity;
- a M\o ller, LSZ or all-time scattering operator;
- gravity, metric BV--BRST transfer, QME restoration or residual transfer;
- anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Verification

All Python, paper and repository-test processes ran sequentially under the
500 MB virtual-memory ceiling.

- Tier 0 passes.  The three Python files compile, the certificate validates
  against its strict Draft-2020-12 schema, an injected additional property is
  rejected, every changed JSON file parses, and the scoped
  `git diff --check` is clean.  Schema validation and compilation took
  `0.07 s` at `21676 KiB` peak RSS.
- The exact producer passes `38/38` checks in `0.03 s` at `16700 KiB`.
  The independent verifier reconstructs the rational parity split, all trace
  weights, the predecessor weak-ghost mismatch and finite pointer
  intertwining without importing the producer; it passes `52/52` checks in
  `0.02 s` at `15684 KiB`.  All `46` adversarial mutation tests pass in
  `0.048 s` (`0.08 s` enclosing wall time) at `18396 KiB`.
- The affected Tier-2 chain passes for the positive-local real-structure,
  auxiliary polynomial quadrupole and auxiliary pointer local-unitary
  certificates.  The complete producer/verifier chain took `0.32 s` at
  `24028 KiB` peak RSS.
- Papers V and VI compile twice with
  `pdflatex -interaction=nonstopmode -halt-on-error`.  Their final PDFs have
  `77` pages and `734507` bytes, and `67` pages and `693076` bytes, with
  SHA-256
  `23c44cdceba834b32ceb93a27503a1007e367818ede995efc6dd34b913fc89fa`
  and
  `ecc7c6c40a615c20ab8091fdcd5791359f2e9c16942b5dfb17b5bd2f910eb5b6`.
  The enclosing two-pass commands completed with final-pass times of
  `0.51 s` at `50980 KiB` and `0.53 s` at `50704 KiB`.  The logs contain no
  undefined citation or reference and no new overfull box.
- Tier 3 is fail-closed, not a repository-wide pass: `3050` tests ran in
  `702.790 s` (`703.82 s` enclosing wall time) at `391396 KiB` peak RSS, with
  `31` failures and `9` skips.  This is the established repository failure
  count; all `46` tests introduced here pass.  The older certificate drift
  and `chain_imports` outside-reference findings remain unresolved and block
  a repository freeze.  No failed or skipped rail is counted as a pass.
- The append-only Science Forge planning fold accepts `1563` nodes with zero
  invalid items and zero malformed events in `5.92 s` at `226264 KiB`.
- The advisory Science Forge shadow wrapper exits zero by design in `1.98 s`
  at `333932 KiB`, but its internal bridge audit remains fail-closed with the
  known Forge binary/standard-library `E9118` mismatch.  Its census reports
  `1621` certificates and `1399` verifier files against the older baseline.
  These advisory findings establish no theorem pass.

Tier 3 was required because Papers V and VI acquire a
`COEFFICIENT_COMPUTED` physical theorem.  No classical freeze, QME state,
shared core operator or `LORENTZIAN-CAUSAL` state changed.  The final
certificate SHA-256 before staging is
`e6a238dc121e8ebe041c463fcf5a3b2b9c4f4d0bc457ec3ede7130e149051bc5`.

## Next gate

Compute the \(\lambda^{10}\) coefficient of this same fixed pointer contrast.
In parallel, apply the fixed-point test to the first dynamically complete
multi-channel public transition operator.  A fixed operator enlarges the
common-Born physical sector; a nonfixed component quantifies the exact
probability obstruction and cannot be averaged away.
