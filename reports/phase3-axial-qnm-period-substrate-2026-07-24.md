# Phase 3 axial QNM-period substrate audit

## Disposition

`READ-ONLY RECONNAISSANCE — SUCCESSOR SPECIFIED, NO QNM RESULT`

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The exact projective-cocycle reduction makes a one-QNM period computation
substantially smaller than the complete six-state transport problem.  The
repository nevertheless does not yet contain a numerical or certified
spin-two QNM disk, a complex-frequency Jost germ, or a hyperboloidal or
complex-scaled scalar Regge--Wheeler solver.  The smallest falsifiable
successor is therefore a scalar, factorized complex-frequency rail, not
another full Bach connection calculation.

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

1. **Certified simple QNM disk.**  No repository artifact gives a numerical
   or enclosed damped spin-two QNM, \(A_{{\rm in},2}'\), or a
   multiplicity-one theorem.
2. **Complex-frequency endpoint germs.**  Horizon-ingoing and
   infinity-outgoing scalar Jost initializers need analytic dependence on
   \(\omega\) and certified tail bounds on the chosen disk.
3. **A convergent QNM contour or Fredholm compactification.**  Direct
   real-axis QNM fields grow at the endpoints.  A hyperboloidal,
   exterior-complex-scaled, or equivalently renormalized realization must be
   fixed with its branches and domains.
4. **Frequency-variational transport.**  Root certification needs a
   validated enclosure of the scalar Evans function and its
   \(\omega\)-derivative.
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

2. **Produce a noncertifying seed.**  Locate a candidate fundamental
   spin-two QNM with two independent high-precision methods, preferably
   matched scalar shooting and hyperboloidal Chebyshev or a Leaver
   recurrence.  Record the result only as `UNVALIDATED-NUMERIC`.

3. **Certify endpoint initializers on a small complex disk.**  Construct
   analytic horizon and infinity Jost heads with ball-valued recurrence
   remainders.  The disk must exclude \(\omega=0\), all declared frame events,
   and any coefficient pole.

4. **Certify one simple spin-two root.**  Match the two scalar Jost columns at
   an interior radius, form their Wronskian \(W(\omega)\), propagate the
   \(\omega\)-variational equations, and apply complex interval
   Newton/Krawczyk or an argument-principle enclosure.  Establish exactly one
   zero and \(0\notin W'\) on the isolating disk.

5. **Exclude a coincident spin-one zero.**  Enclose
   \(A_{{\rm in},1}\) on the same disk and prove that it does not contain zero.
   Otherwise the three-factor local Smith problem is a different case.

6. **Evaluate the projective period.**  Transport the symmetric-square
   state
   \[
   y^2,\qquad yDy,\qquad (Dy)^2
   \]
   together with a period accumulator.  This is a linear augmented system
   because the symmetric-square variables obey \(\mathcal K_Uz=0\).
   Add the certified endpoint term \(B_n\) and enclose \(\beta_n\) over the
   root disk on the chosen hyperboloidal or complex-scaled contour.

7. **Compute the independent Fitting selector.**  Enclose the normalized
   factor-frame minor \(\Delta=bf\) at the same disk and verify the exact
   normalization relation between \(\Delta\) and the projective period.  The
   two computations serve as independent end-to-end checks rather than
   interchangeable definitions.

8. **Apply the claim gate.**  Only if the root is simple, the spin-one factor
   is a unit, the independent rails agree, and the \(\beta_n\) or normalized
   Fitting-minor enclosure excludes zero may the connection Smith type be
   promoted to \((0,0,2)\).  A second-order differential Green-resolvent pole
   additionally requires the declared analytic Fredholm realization.

## Fail-closed outcomes

- Failure of interval Newton or an argument-principle enclosure does not
  disprove a QNM.
- A disk containing zero or several roots does not prove nonsimplicity; it
  requires subdivision or a better analytic frame.
- An endpoint recurrence refusal or noncontractive tail is a substrate
  shortfall, not a physical singularity.
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

The cheapest binary selector remains the normalized factor-frame Fitting
minor.  The projective period is nevertheless the cleanest invariant
interpretation and the strongest independent verification rail.  The
implementation should therefore certify the scalar QNM disk first, then
compute both objects on the same disk and require their normalization
crosswalk before promotion.

CLOSE-OUT: SHORTFALL — the exact scalar target and smallest falsifiable successor are identified, but no QNM germ, period, nonzero selector or Smith case is computed.
MISSING-DEP: certified complex-frequency scalar RW endpoint germs and a simple QNM disk with a convergent projective-period normalization
