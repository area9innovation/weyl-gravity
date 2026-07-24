# Phase 3 axial QNM-period substrate audit

## Disposition

`READ-ONLY RECONNAISSANCE — SUCCESSOR SPECIFIED, NO QNM RESULT`

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The exact projective-cocycle reduction makes a one-QNM extension computation
substantially smaller than the complete six-state transport problem.  The
repository nevertheless does not yet contain a numerical or certified
spin-two QNM contour, a complex-frequency Jost germ, or a hyperboloidal or
complex-scaled scalar Regge--Wheeler solver.  The smallest falsifiable
successor is therefore a scalar, factorized complex-frequency rail, not
another full Bach connection calculation.

The primary rail should be root-free: certify that a contour \(D\) contains
one scalar QNM by the argument principle and then certify a nonzero contour
moment of the repeated-factor extension.  This avoids evaluating an interval
extension coefficient at an interval root, where loss of the shared
root/function correlation can make a decisive nonzero result artificially
contain zero.  Direct projective-period and Fitting-minor computations remain
necessary as independent rails.

This report inventories reusable inputs, identifies the typed gaps, and
specifies the proposed
`axial_qnm_fundamental_projective_period_v1` successor.  It creates no
certificate and makes no inference about the value or sign of any physical
QNM period.

## Reusable exact and classified inputs

### Projective cocycle

`black_hole_programme/phase3/axial_qnm_projective_cocycle_v1/certificate.json`
contains the exact Liouville-normal-form potential, scalar source and reduced
projective cocycle:

\[
D=\frac{r-2}{r}\partial_r,\qquad
L=D^2+U,
\]

\[
U=\frac{\omega^2r^4-6r^2+18r-12}{r^4},
\]

\[
\mathcal I_{\rm red}
=
\frac{i(r-2)(2\omega^2r+3\omega^2+12)}
     {5\omega r^4}.
\]

It also supplies the exact nontriviality result

\[
[\mathcal I]\ne0
\quad\text{in}\quad
\mathbb C(i,\omega)(r)/
\mathcal K_U\mathbb C(i,\omega)(r),
\qquad
\mathcal K_U=D^3+4UD+2DU,
\]

and the negative angular-deformation comparison.  At the time of this audit,
this package exists in the shared worktree but is not tracked by Git.  It must
be independently verified and integrated before a successor treats it as an
authoritative imported artifact.

### Local Smith and Fredholm logic

`black_hole_programme/phase3/axial_qnm_local_smith_dichotomy/certificate.json`
provides:

- the exact local Smith/Fitting dichotomy at a simple spin-two zero;
- the normalized factor-frame minor selector;
- the frame-invariant second Fitting ideal;
- the conditional analytic-Fredholm principal part;
- the exact separation between an inverse-connection theorem and a
  differential-resolvent theorem.

It does not evaluate \(\beta_n\), select a QNM Smith case, or construct the
physical Fredholm realization.

`black_hole_programme/phase3/axial_spin_two_scattering_extension_preflight/`
provides the exact rank-one repeated-spin-two extension and an explicit
missing-QNM ledger.  Its older notation for the repeated-factor connection
entry should be read through the corrected local-Smith package.

### Differential filtration and boundary convention

`black_hole_programme/phase3/axial_rw_lx_triangular_preflight/certificate.json`
provides the exact RW/RW/spin-one filtration, the rational inclusions and
quotients, and the two scalar potentials.

`black_hole_programme/phase3/axial_boundary_devissage_no_growth/certificate.json`
fixes:

- the time convention \(\exp(+i\omega t)\);
- the damped QNM half-plane \(\operatorname{Im}\omega>0\);
- the future-horizon-regular and pure-outgoing infinity boundary classes;
- the intrinsic factor Evans product
  \(A_{{\rm in},2}^2A_{{\rm in},1}\);
- the distinction between separated-mode no-growth and the open damped QNM
  problem.

`black_hole_programme/phase3/axial_incoming_connection_analytic/certificate.json`
provides the exact spin-two potential, Jost normalization and real-frequency
Wronskian theorem.  It contains formal amplitude symbols and existence
theorems, not computed Jost germs.

### Complex-frequency and validation contracts

`black_hole_programme/certificates/BH3_ANALYTIC_CONTINUATION_GATE.json`
provides coefficientwise meromorphic continuation, the exact Frobenius
frame-event ledger, and the joint analytic strip

\[
|\operatorname{Im}\omega|<\frac14,\qquad \omega\ne0.
\]

It explicitly does not establish convergence or summability of the infinity
series off the real axis.

`black_hole_programme/certificates/BH3_NUMERICAL_VALIDATION_PROTOCOL.json`
is the mandatory validation contract for any prospective complex-frequency
or QNM computation.  It requires two independent implementations,
real-frequency anchor reproduction, declared convergence and residual tests,
and fail-closed disagreement handling.

### Endpoint and finite-interval numerical techniques

The following real-frequency packages contain reusable methods, but their
certified domains do not include a QNM disk:

- `black_hole_programme/phase3/axial_endpoint_remainder_enclosures/`
  contains exact Frobenius heads, horizon Cauchy majorants, and infinity
  Volterra envelopes on real \(\omega\in[1/2,3/4]\).
- `black_hole_programme/phase3/axial_infinity_practical_transfer/`
  contains a phase-normalized \(z=1/r\) transfer with a continuous
  \(z=0\) extension, again only on a declared real-frequency cell.
- `black_hole_programme/phase3/validated_connection_preflight/` contains a
  representative uncontrolled complex RK4 observation and the historical
  substrate gap.  Its numerical values are not enclosures.
- `black_hole_programme/phase3/axial_global_connection_numeric_preview/`
  is explicitly `UNVALIDATED-NUMERIC`, real-frequency only, and supplies no
  QNM information.
- `black_hole_programme/phase3/axial_spin_two_reflection_cell/` currently
  exists as an untracked real-frequency shortfall.  It records that direct
  interval boxing of the oscillatory \(x,\omega\) interaction coefficients
  loses the needed correlation.  Its observations are not evidence.

The Forge libraries
`math/ivmat`, `math/ivlinode`, `math/ivendpoint`, `math/ivaffine` and
`math/ivtaylor` now provide validated finite-interval realified linear
transport, endpoint-tail interfaces and one-generator correlated Taylor
models.  They do not provide complex-frequency exponential dichotomies,
automatic validated QR, or a two-real-parameter correlated complex-frequency
model.

The current Python environment contains `python-flint 0.9.0`, including
`acb` ball arithmetic and certified complex contour integration.  No tracked
black-hole package currently adapts it to Regge--Wheeler Jost transport,
complex root isolation or QNM periods, so its availability is substrate
reconnaissance rather than scientific evidence.

## Missing typed inputs

A decisive one-QNM computation still needs all of the following.

1. **Certified one-QNM contour.**  No repository artifact gives a numerical
   or enclosed damped spin-two QNM contour on whose boundary the scalar Evans
   function is nonzero, or an argument-principle multiplicity-one theorem.
2. **Complex-frequency endpoint germs.**  Horizon-ingoing and
   infinity-outgoing scalar Jost initializers need analytic dependence on
   \(\omega\) and certified tail bounds on the closure of the chosen contour.
3. **A convergent QNM contour or Fredholm compactification.**  Direct
   real-axis QNM fields grow at the endpoints.  A hyperboloidal,
   exterior-complex-scaled, or equivalently renormalized realization must be
   fixed with its branches and domains.
4. **Frequency- and extension-tangent transport.**  The contour count needs
   \(a'(\omega)\), while the extension moment needs the horizon and infinity
   response columns \(X_H,X_+\) satisfying the inhomogeneous repeated-factor
   transport.  Their endpoint initializers and tails must use the same
   analytic normalization as the scalar columns \(Y_H,Y_+\).
5. **Projective-period endpoint normalization.**  The endpoint term \(B_n\)
   and the exact identity
   \[
   \beta_n=B_n+\int_\Gamma\mathcal I_{\rm red}y_n^2\,dr_*
   \]
   must be derived in the selected QNM normalization.
6. **Adjoint/Fredholm identification.**  The transpose-dual scalar germ and
   the physical analytic-Fredholm pairing must be constructed before the
   period is called the full differential-resolvent obstruction.
7. **Period/minor crosswalk.**  The normalized cocycle period must be related
   exactly to the factor-frame Fitting minor.  Nonvanishing of either object
   cannot be transferred by an unspecified normalization.
8. **Independent rail.**  The mandatory BH3 protocol requires a second
   implementation and real-axis anchor reproduction before an off-axis
   result is promoted.

## Proposed successor

### `axial_qnm_fundamental_projective_period_v1`

The successor should be implemented in eight fail-closed stages.

1. **Freeze the scalar contract.**  Import by content hash the certified
   \(U\), \(\mathcal I_{\rm red}\), differential filtration, time convention,
   QNM boundary classes and analytic frame-event ledger.  Derive the
   horizon/outgoing residual equations independently.

2. **Produce a noncertifying seed and contour.**  Locate a candidate
   fundamental spin-two QNM with two independent high-precision methods,
   preferably matched scalar shooting and hyperboloidal Chebyshev or a Leaver
   recurrence.  Choose a small enclosing disk \(D\), but record the seed and
   disk only as `UNVALIDATED-NUMERIC`.

3. **Certify analytic endpoint initializers on \(\overline D\).**  Construct
   horizon-ingoing and infinity-outgoing scalar columns \(Y_H,Y_+\), their
   frequency tangents, and the corresponding extension-response columns
   \(X_H,X_+\), all with ball-valued recurrence remainders.  The closure of
   \(D\) must exclude \(\omega=0\), all declared frame events and every
   coefficient or normalization pole.  Analyticity of these endpoint germs
   is a prerequisite for both contour integrals; the existing real-frequency
   endpoint packages do not supply it.

4. **Propagate the four columns on the contour and form determinant
   tangents.**  At a fixed interior match point propagate
   \[
   Y_H,\quad Y_+,\quad X_H,\quad X_+
   \]
   on each certified contour panel, with
   \[
   Y'=AY,\qquad X'=AX+\mathcal E Y.
   \]
   In a fixed analytic factor normalization define
   \[
   a(\omega)=\det(Y_H,Y_+)
   \]
   and obtain the repeated-spin-two tangent coefficient from
   \[
   b_{\rm tan}(\omega)
   =
   \det(X_H,Y_+)+\det(Y_H,X_+).
   \]
   The exact factor-frame derivation must identify
   \(b_{\rm tan}\) with the triangular entry \(b\), possibly up to a declared
   analytic unit and an \(a\)-multiple.  Likewise compute
   \[
   a'=
   \det(\partial_\omega Y_H,Y_+)
   +\det(Y_H,\partial_\omega Y_+)
   \]
   from the frequency-variational transport rather than finite differences.

5. **Certify the root count without enclosing the root.**  Prove
   \(0\notin a(\partial D)\), then enclose
   \[
   N_D=
   \frac{1}{2\pi i}
   \oint_{\partial D}\frac{a'(\omega)}{a(\omega)}\,d\omega
   \]
   tightly enough to certify the exact integer \(N_D=1\).  This establishes
   that \(D\) contains one spin-two zero counted with multiplicity and hence
   one simple QNM.  On the same closure, certify that the spin-one incoming
   coefficient has no zero; otherwise the full three-factor local Smith
   problem replaces the two-factor dichotomy.

6. **Certify the root-free extension moment.**  In the same analytic
   normalization enclose
   \[
   K_0=
   \frac{1}{2\pi i}
   \oint_{\partial D}\frac{b(\omega)}{a(\omega)}\,d\omega.
   \]
   With \(N_D=1\), no spin-one zero and no frame pole in \(D\),
   \[
   K_0=\operatorname*{Res}_{\omega=\omega_n}\frac{b}{a}
      =\frac{b(\omega_n)}{a'(\omega_n)}.
   \]
   Therefore \(0\notin K_0\) proves \(b(\omega_n)\ne0\) and selects the
   defective local Smith case without ever evaluating \(b\) on an
   interval-valued root.  This is the primary falsifiable rail.

   The zero/nonzero conclusion is normalization invariant.  Multiplying the
   scalar endpoint columns by analytic nonvanishing units multiplies \(a\)
   and \(b\) by their common unit, leaving \(b/a\) unchanged.  An admissible
   triangular response-frame shear changes
   \[
   b\longmapsto b+a\,h
   \]
   with \(h\) analytic, so \(b/a\mapsto b/a+h\) and the closed-contour moment
   is unchanged.  More general compatible factor-frame changes may multiply
   the residue by a nonvanishing analytic unit; they preserve its
   nonvanishing, while its numerical value remains tied to the frozen
   normalization.  Similarly, \(a\mapsto u a\) adds \(u'/u\) to \(a'/a\);
   its contour integral vanishes when \(u\) is a unit on \(D\).

7. **Run two independent selector rails.**

   - For the direct projective-period rail, transport the symmetric-square
     state
   \[
   y^2,\qquad yDy,\qquad (Dy)^2
   \]
   together with a period accumulator.  This is a linear augmented system
   because the symmetric-square variables obey \(\mathcal K_Uz=0\).
   After separately isolating the root inside \(D\), add the certified
   endpoint term \(B_n\) and enclose \(\beta_n\) on the chosen hyperboloidal
   or complex-scaled realization.  This rail retains the harder
   root/function correlation problem deliberately: it is an independent
   check of the root-free contour decision, not the primary selector.

   - For the Fitting rail, compute the normalized full-connection selector
     \(\Delta=bf\) independently of the determinant-tangent construction.
     Verify the exact normalization relations among \(K_0\), \(\Delta\) and
     the projective period.  These are independent end-to-end checks, not
     interchangeable definitions.

8. **Apply the claim gate.**  Only if \(N_D=1\), the spin-one factor is a unit,
   \(0\notin K_0\), the independent period and Fitting rails agree, and every
   endpoint and normalization audit passes may the connection Smith type be
   promoted to \((0,0,2)\).  A second-order differential Green-resolvent pole
   additionally requires the declared analytic Fredholm realization.

## Fail-closed outcomes

- Failure of the argument-principle enclosure, or of an optional interval
  Newton refinement, does not disprove a QNM.
- A contour on which \(a\) cannot be certified nonzero is invalid for the
  argument principle; it is not evidence for a QNM on the contour.
- A count enclosure that does not isolate the integer \(1\) is inconclusive.
  A count different from one does not by itself classify multiplicities
  until poles and frame events have also been excluded.
- An endpoint recurrence refusal or noncontractive tail is a substrate
  shortfall, not a physical singularity.
- A \(K_0\) enclosure containing zero is inconclusive.  It does not prove
  \(b(\omega_n)=0\) or select the semisimple Smith case.
- A nonzero \(K_0\) obtained without certified analytic endpoint germs,
  boundary nonvanishing of \(a\), and exclusion of internal frame poles is
  not a residue certificate.
- A \(\beta_n\) enclosure containing zero is inconclusive.  It does not prove
  \(\beta_n=0\) or select the semisimple Smith case.
- A Fitting-minor enclosure containing zero is likewise inconclusive.
- A coincident spin-one zero invalidates the two-factor reduction and must be
  classified with the full three-factor local Smith problem.
- Disagreement between the period and minor normalizations blocks promotion.
- Disagreement between the two numerical rails blocks every QNM, EP2 and
  ringdown claim.
- A certified connection-level Smith type is not by itself a
  differential-resolvent or spacetime Green-function theorem.
- No result in this successor would establish time-domain stability,
  completeness, a quantum state, CPT positivity, particles or unitarity.

## Recommended implementation order

The cheapest robust binary selector is the root-free contour moment.  The
implementation should certify analytic endpoint germs on a candidate
contour, establish \(N_D=1\), and then enclose \(K_0\) using the same
contour-panel transport.  This preserves the correlation between \(a\) and
\(b\) pointwise on the contour while avoiding the harder and unnecessary
correlation between a two-dimensional interval root and a separately
evaluated function at that root.

The direct projective period remains the cleanest invariant interpretation,
and the normalized full-connection Fitting minor remains the strongest
independent algebraic selector.  Both should be run after the contour rail
and must reproduce its zero/nonzero decision through an exact normalization
crosswalk before promotion.

CLOSE-OUT: SHORTFALL — the exact scalar target and root-free contour successor are identified, but no QNM contour, contour moment, period, nonzero selector or Smith case is computed.
MISSING-DEP: certified analytic complex-frequency scalar and extension endpoint germs on a one-QNM contour, plus a convergent projective-period normalization
