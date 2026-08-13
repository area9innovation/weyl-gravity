# Standard BT characteristic projector: Eq. (19) inheritance and doubled repair

**Certificate:**
`REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
**Lifecycle:** `CLASSIFIED`.

## Result

The actual normalized three-particle characteristic projector does not evade
the finite-regulator charge--squeeze obstruction.  It inherits it with an
eightfold species multiplicity.  Consequently the proposed
order-\(\lambda^2\) standard-projector comparison with the completed
\(q_{10}\) functional is blocked by an earlier coefficient:

- in the fixed-vacuum grading the order-\(\lambda\) pushforward contains a
  positive-charge component of rank 16;
- in the covariant grading the whole free pushed projector is neutral, but its
  ghost-odd part has exact nonzero relative norm
  \[
  -4z^2(z^2+2),
  \]
  equal to \(-33/64\) at the normalized finite-box amplitude \(z=1/4\); and
- every other homogeneous orbit-charge assignment has positive free squeeze
  support.

This closes the public regular **one-sheet** test for the standard \(n=3\)
projector.  It is no longer correct to treat its order-\(\lambda^2\)
pushforward as the next calculation: an order-\(\lambda^2\) term cannot cancel
a nonzero order-\(\lambda^0\) parity defect.

There is also a constructive result.  The direct sum of the pushed projector
and its parity conjugate on two explicitly declared sheets is exactly neutral,
idempotent, Krein self-adjoint and ghost even.  Averaging the trace over the
two sheets preserves the original finite \(q_8\)--\(q_{10}\) jet.  This is a
complete algebraic repair of the charge/parity conflict, but it changes the
source theory.  No public BT datum derives the second sheet, and stationarity,
asymptotic domains and the continuum trace remain open.

## Why the public \(1/3!\) does not suppress the obstruction

The standard scalar projector is

\[
 P_\chi^{(\phi)}={1\over3!}\int(d_4p)^3\,
 \chi(p)\widetilde W(p)|\widetilde\Psi(p)\rangle
 \langle\widetilde\Psi(p)|.
\]

For the certified point cell the three momenta are distinct.  An
identical-particle characteristic contains all six disjoint \(S_3\) images,
so

\[
 {6\over3!}=1.
\]

That cancellation normalizes the unordered momentum cell.  It does not
identify the target-field species assignments.  Each active momentum has the
two-dimensional public fibre
\(\operatorname{span}\{\Omega,\Upsilon\}\), so the neutral three-particle
species block is

\[
 \bigl(\mathbb C^2\bigr)^{\otimes3},\qquad \operatorname{rank}P_3=2^3=8.
\]

Choose one unordered nonzero momentum pair outside the compact
characteristic support and its antipodes.  The Appendix-C squeeze on that
pair factors from the active projector.  Thus every trace contraction and
every support rank is multiplied by eight.

## Exact free squeeze inheritance

On the pair basis

\[
 (|0\rangle,|\Omega\Omega\rangle,|\Upsilon\Upsilon\rangle)
\]

use

\[
 J=\kappa=\begin{pmatrix}1&0&0\\0&0&1\\0&1&0\end{pmatrix},
 \qquad
 Q=\begin{pmatrix}0&-z&0\\0&0&0\\z&0&0\end{pmatrix},
 \qquad Q^3=0.
\]

The exponential is exact and the squeezed vacuum projector has Laurent
support \(1,Z^2,Z^4\).  Its canonical parity-odd part has support
\(Z^{-4},Z^{-2},Z^2,Z^4\), ranks \((1,2,2,1)\), and relative norm

\[
 \tau_0(C_{\rm pair}^\sharp C_{\rm pair})
 =-{z^2(z^2+2)\over2}.
\]

Tensoring with \(P_3\) gives support ranks

\[
 (8,16,16,8)
\]

and

\[
 \boxed{
 \tau_0(C_3^\sharp C_3)=-4z^2(z^2+2).}
\]

The even--odd overlap remains zero.  At \(z=1/4\),

\[
 \boxed{\tau_0(C_3^\sharp C_3)=-{33\over64}\ne0.}
\]

The defect is therefore neither absent nor a null term that could be dropped
from the generalized Born trace.

## Exhaustion of homogeneous charge

The complete public factorization has locked charges

\[
 q_K=1-s,\qquad q_S=2s-2=-2q_K.
\]

For \(s<1\), let the certified rank-four nonlinear tangent act on one active
particle and tensor it with the other two rank-two species fibres and the
disjoint pair vacuum.  The resulting positive-charge component has rank

\[
 4\cdot2\cdot2=16.
\]

It cannot be canceled by components of different charge.  This includes the
public fixed-vacuum assignment \(s=0\).

For \(s>1\), the one-pair and two-pair free squeeze coefficients have ranks
two and one.  Tensoring with the active rank-eight block gives positive-charge
ranks 16 and 8.

Only \(s=1\) avoids positive support.  Then the covariant all-order charge
theorem makes the complete pushforward neutral, so the strictly negative
remainder in Eq. (19) is zero.  The full neutral term must itself be ghost
even, contradicted by \(-33/64\) above.  The three cases exhaust every real
homogeneous \(s\).

## Consequence for the completed \(q_{10}\) calculation

The completed selected experiment has

\[
 q[F]=\lambda^8q_8[F]+\lambda^{10}q_{10}[F]+O(\lambda^{12}),
\]

with positive \(q_8\), exact finite \(q_{10}\), common public/Hilbert Born
form and the correct order-\(\lambda^{10}\) renormalization-group
cancellation.  None of that is invalidated.

What fails is the proposed identification of that selected shift-breaking
experiment with the standard shift-invariant one-sheet projector.  In the
covariant architecture the standard projector already fails ghost parity at
\(\lambda^0\).  Formal power series are coefficientwise identities, so its
order-\(\lambda^2\) correction cannot repair the zeroth-order coefficient.
The one-sheet comparison is therefore

\[
 \boxed{\text{BLOCKED BEFORE THE }q_{10}\text{ COEFFICIENT}.}
\]

## Canonical doubled parity completion

The obstruction identifies its own smallest direct-sheet repair.  Let

\[
 A=R_tP_\chi^{(\phi)}R_t^\dagger
\]

on the covariant formal algebra and introduce a second declared source and
target sheet.  Put

\[
 A_{\rm dbl}=A\oplus\kappa A\kappa
\]

and define doubled ghost parity by

\[
 K_{\rm dbl}(v,w)=(\kappa w,\kappa v),
\]

together with inversion of the Laurent orbit.  Block algebra gives

\[
 A_{\rm dbl}^2=A_{\rm dbl},\qquad
 A_{\rm dbl}^\sharp=A_{\rm dbl},\qquad
 K_{\rm dbl}A_{\rm dbl}K_{\rm dbl}=A_{\rm dbl}.
\]

At \(s=1\), both summands are neutral to all formal orders, so
\(Q_{\rm negative}=0\).  On the finite \(n=3\) block the raw trace doubles
from 8 to 16.  The natural sheet-averaged trace

\[
 \tau_{\rm dbl}(X\oplus Y)={\tau(X)+\tau(Y)\over2}
\]

recovers \(\tau_{\rm dbl}(A_{\rm dbl})=8\).  Because the selected tree and
loop tensors are each \(\kappa\)-fixed, the same identity preserves

\[
 \lambda^8q_8+\lambda^{10}q_{10}.
\]

This is an exact algebraic escape from the charge--parity dichotomy.  It is
not the public Eq. (19): the second sheet is supplied as new data, not derived
from \(R_t\) or the scalar source.  Calling it a hidden BT particle or a new
physical dimension would be unjustified.

## Boundary and next gate

Established:

- exact normalization of the standard \(n=3\) characteristic cell;
- rank-eight active species fibre;
- inheritance of all three homogeneous charge cases;
- positive ranks 16 for \(s<1\), and 16 and 8 for \(s>1\);
- exact covariant ghost-odd norm \(-4z^2(z^2+2)\);
- the finite-box value \(-33/64\);
- failure before any order-\(\lambda^2\) \(q_{10}\) comparison;
- an exact two-sheet neutral ghost-even formal projector; and
- preservation of the sheet-normalized finite \(q_8\)--\(q_{10}\) trace.

Not established:

- the public one-sheet Eq. (19);
- a derivation of the second sheet from the BT scalar theory;
- time independence of the complete doubled neutral term;
- \(t\to\pm\infty\), continuum or trace-domain control;
- affiliation between the standard projector and the selected packet ideal;
- finite-coupling or all-channel probability;
- any metric BV--BRST, QME, gravity or `LORENTZIAN-CAUSAL` result; or
- literature priority.

The next decisive question is whether the conjugate branch can be supplied
without changing the source theory.  A constructive route needs a localized
or singular source parity with controlled domain and adjoint.  A negative
route must prove that every vacuum-retaining source-affiliated completion
contains an independent parity-conjugate sector.  Only after that gate passes
does time independence and the asymptotic standard-projector trace become the
right calculation.

## Verification receipt

All scientific Python and TeX commands ran sequentially under
`ulimit -v 500000`.  The repository-wide rail additionally used the sanitized
`PATH=/usr/local/bin:/usr/bin:/bin`.

| Tier | Command or rail | Result | Elapsed | Peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and JSON parse | PASS | 0.02 s each | 15,240 KiB |
| 0/1 | exact producer `--write --check` | PASS, 37/37 | 0.43 s | 69,144 KiB |
| 1 | fraction-polynomial independent verifier and strict schema | PASS, 38/38 | 0.08 s | 24,188 KiB |
| 1 | focused adversarial suite | PASS, 16 tests | 1.52 s | 69,332 KiB |
| 2 | five predecessor verifiers plus the new verifier | PASS, 26/26, 45/45, 25/25, 39/39, 54/54 and 38/38 | 1.12 s total | 70,084 KiB |
| 2 | combined affected tests | PASS, 138 tests | 18.71 s | 70,308 KiB |
| 0 | Paper V, two `pdflatex` passes | PASS | 0.53 s, 0.52 s | 50,916 KiB maximum |
| 0 | Paper VI, two `pdflatex` passes | PASS | 0.54 s, 0.52 s | 50,872 KiB maximum |
| 2 | Science Forge planning import/fold | PASS, 1,585 nodes; 0 invalid items; 0 malformed events | 7.59 s | 294,576 KiB |
| 3 | full `unittest discover` | **FAIL-CLOSED**, 3,459 tests: 31 failures, 9 skips | 709.861 s (710.91 s rail) | 391,516 KiB |

The Tier-3 total increased by exactly the sixteen new tests relative to the
preceding 3,443-test run.  The failure count and skip count are unchanged.
All failures remain in older certificate/hash-drift families and the two
existing `chain_imports` assertions; the new producer, verifier and tests do
not occur in the failure list.  The repository-wide rail is not called a pass
and promotes no freeze.

The advisory Science Forge shadow rail completed in 2.05 s at 335,740 KiB.
It inventories 1,632 certificates and 1,413 verifier files, while retaining
the known Forge 0.0.2/stdlib mismatch, bridge-audit E9118 and baseline corpus
drift.  Its advisory exit zero is not certified success.

Paper V has 82 pages, 765,787 bytes and SHA-256
`feb6b5f3c9acb4e7352fc5866ca63053223d0f7e8fed01c6ca5ab6a474d78762`.
Paper VI has 71 pages, 728,776 bytes and SHA-256
`675d0341d877dd9b7897f2dd24b71c66d3d7b56d9738457aa7ade5e238e09232`.
There are no undefined references; every overfull-box warning lies outside
the new passages.  The certificate SHA-256 is
`3a11135e76857212c92ca1797dd0dd78dfa4e3e1fb68a3e3462cfdc958075d45`.

CLOSE-OUT: DONE -- the actual normalized three-particle characteristic
projector inherits the public one-sheet Eq. (19) obstruction, while a canonical
two-sheet parity completion solves the finite formal charge/parity problem but
changes the source theory and does not yet establish physical affiliation.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1.json`
