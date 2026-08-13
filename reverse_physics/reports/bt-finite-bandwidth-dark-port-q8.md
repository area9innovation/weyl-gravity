# BT finite-bandwidth dark-port probability at order lambda eight

Certificate:
`REVERSE_PHYSICS_BT_FINITE_BANDWIDTH_DARK_PORT_Q8_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED` on a nonempty globally normalizable
finite-total-momentum and invariant-mass packet class.

## Result

The compact-sphere dark-port coefficient survives finite bandwidth in total
momentum and invariant mass.  The new packet is an ordinary compactly
supported \(L^2\) vector in the two-body direct integral, rather than a vector
on one sharp total-momentum fibre.

The certified bound is

\[
 \boxed{
 {Q_{8,-}^{\rm band}\over\bar q_{4,\rm band}}
 >{2401\over9136478748672}>{1\over10^{10}}.}
\]

The bandwidth is an existence result: one sufficiently small compact hard
neighborhood is proved to work, but its radius is not numerically evaluated.
This is enough to prove global wavepacket normalizability.  It is not yet a
quantitative beam or apparatus design.

## Why the off-diagonal loop was the missing object

The fixed-fibre predecessor used equal incoming and outgoing total energy.
For a packet with invariant-mass thickness, an incoming component and an
outgoing component can instead differ by

\[
 \Omega=E_{\rm out}-E_{\rm in}.
\]

The first-Dyson tree then carries the switching factor

\[
 F_T(\Omega)=\int_0^T e^{i\Omega t}\,dt.
\]

A statement using only the energy-diagonal loop would therefore leave out a
term of the same perturbative order as the claimed probability.  The present
calculation derives that term rather than assuming it is continuous.

Put

\[
 x=\Omega T,\qquad y=\delta T,
\]

where \(\delta\) is the intermediate-state energy defect, and define

\[
 f(x)=\int_0^1e^{ixt}\,dt
     =e^{ix/2}\operatorname{sinc}(x/2).
\]

The ordered two-vertex factor is

\[
 d(x,y)=\int_0^1dt_1\int_0^{t_1}dt_2\,
 e^{iyt_1+i(x-y)t_2}.
\]

Doing the \(t_2\) integral gives the exact divided difference

\[
 \boxed{d(x,y)={f(x)-f(y)\over i(x-y)}.}
\]

The apparent value at \(x=y\) is removable.  The normalized real tree-loop
interference kernel is

\[
 k(x,y)={\operatorname{Im}\{\overline{f(x)}d(x,y)\}
             \over|f(x)|^2}
 ={1-\cos((y-x)/2)\operatorname{sinc}(y/2)/
              \operatorname{sinc}(x/2)\over y-x}.
\]

On the energy diagonal this becomes

\[
 k(0,y)={1\over y}-{\sin y\over y^2},
\]

which is exactly the sharp-time kernel used by the certified diagonal loop.
The producer verifies every ordered-simplex monomial through total degree
twelve.  The independent verifier instead substitutes \(t_2=t_1u\) and uses
the beta integral; at total degree \(N\), every \(x^p y^{N-p}\) coefficient,
with the common \(i^N\) removed, is

\[
 {1\over(N+2)!}.
\]

This establishes the divided difference by two algebraically distinct rails.

## The ultraviolet comparison

For \(|x|\leq1/2\), the elementary alternating bound gives

\[
 \operatorname{sinc}(x/2)\geq {95\over96}>0.
\]

Rewrite the kernel as

\[
 k(x,y)={1\over y-x}-{N(x,y)\over y(y-x)},
\]

where

\[
 N(x,y)={\sin(y-x/2)+\sin(x/2)\over
                 \operatorname{sinc}(x/2)}.
\]

For \(|y|\geq1\), one has \(|y-x|\geq|y|/2\).  Differentiating the integral
form of the sinc function gives

\[
 |N(x,y)-\sin y|\leq {6\over5}|x|.
\]

Separating the divided-difference denominator from the oscillatory numerator
then yields the exact uniform estimate

\[
 \boxed{
 |k(x,y)-k(0,y)|\leq {32\over5}{|x|\over y^2}.}
\]

The diagonal kernel has the logarithmically divergent \(1/y\) ultraviolet
term.  The displayed estimate proves that this term is independent of the
external mismatch.  On compact external momentum support, the radial density
of the massless two-particle old-fashioned spectral representation is bounded
at large loop momentum, while \(|y|\) grows linearly.  The off-diagonal minus
diagonal remainder is consequently dominated by an integrable constant
times \(dq/q^2\).

It follows that the same local \(\overline{\rm MS}\) counterterm already fixed
on the energy diagonal renormalizes the off-diagonal kernel.  No
mismatch-dependent counterterm is introduced.  On a finite loop-momentum
region, the ordered-simplex integral is jointly continuous and bounded.  The
renormalized hard loop is therefore jointly continuous in incoming and
outgoing external momenta.  Intermediate resonances and the timelike cut are
included: the ordered-simplex expression has no energy-denominator pole, and
their contribution approaches the certified diagonal value continuously.

## Thickening the direct integral

At the central fibre

\[
 P_0=(8\kappa/5,\mathbf0),\qquad \kappa T=1,
\]

the compact-sphere certificate gives

\[
 \Delta R_6>{49\over534336}.
\]

After the common spatial conservation delta is reduced, use local hard
coordinates consisting of the common total spatial momentum, the positive
incoming and outgoing invariant masses, the two-body angular coordinates and
the spectator variables.  The two-body coarea is a positive smooth multiple
of

\[
 d^3\mathbf P\,dM_{\rm in}\,dM_{\rm out}\,
 d\Omega_{\rm in}\,d\Omega_{\rm out}
\]

in a neighborhood of the central future-timelike point, tensored with the
normalized spectator measure.

The connected finite-time tree is continuous because its switching functions
are entire and every hard denominator stays separated from zero.  The active
loop is continuous by the ultraviolet theorem above.  Keep the central
angular, incoming and spectator packet shapes fixed and multiply them by a
normalized compact bump envelope in the direct-integral total-momentum and
mass variables.  As those radial supports shrink, the \(q_4\) and \(q_6\)
bilinear forms carry the same positive coarea scaling, while their quotient
converges to the fixed-fibre packet quotient; its \(q_4\) denominator is
strictly positive.  Uniform continuity therefore supplies one nonempty
product neighborhood on which

\[
 \Delta R_6^{\rm band}>{1\over2}{49\over534336}
 ={49\over1068672}.
\]

Choose any nonzero normalized compact (L^2) bump envelope inside that
neighborhood and transport the two equal-area angular cells fibrewise.  This
is an ordinary globally normalized direct-integral wavefunction.  The contact
leading kernel and \(F_T(\Omega)\) are common to the two angular cells on
each fibre, so their antisymmetric dark projector annihilates \(X_2\)
pointwise, not merely at the central momentum.

The packetwise \(q_6\) identity and Cauchy--Schwarz now give

\[
 {Q_{8,-}^{\rm band}\over\bar q_{4,\rm band}}
 \geq{(\Delta R_6^{\rm band})^2\over8}
 >{2401\over9136478748672}>{1\over10^{10}}.
\]

The smaller decimal comparison relative to the fixed-fibre theorem is the
explicit price of retaining only half the certified continuity margin.  It is
not a numerical estimate of the attainable experimental coefficient.

## Physical boundary

This closes the mathematical normalizability layer for the selected BT
dark-port probability coefficient.  It establishes a nonempty class of
finite-total-momentum and finite-invariant-mass wavepackets and includes the
off-energy-diagonal loop at the required order.

It does not provide a numerical bandwidth, a canonical envelope, compact
spacetime support, a local apparatus selecting the fibrewise projector, the
recorded or symmetric bright-port absolute coefficient, control of the
\(O(\lambda^{10})\) remainder, forward/collinear/KLN completion, an all-time
scattering operator, general Eq. (19), a complete positive BT Hilbert/Fock
space, a metric BV--BRST gravity transfer, a restored QME, residual transfer,
or anything `LORENTZIAN-CAUSAL`.  No literature-priority claim is made.

The next physical step is quantitative rather than existential: bound one
explicit smooth compact envelope, or the already certified Gaussian
apparatus, inside the continuity neighborhood.  The next perturbative step is
then either the order-\(\lambda^{10}\) dark remainder or the still-unknown
recorded/bright \(q_8\) coefficient.  General Eq. (19) remains the separate
architectural route.

## Verification receipt

All scientific Python and TeX processes ran sequentially under
`ulimit -v 500000`.

- Tier 0 Python compilation and JSON parsing: PASS in 0.03 s at 14,476 KB
  peak RSS.
- Exact producer replay: PASS 29/29 in 0.03 s at 16,448 KB peak RSS.
- Method-distinct beta-simplex and ultraviolet verifier: PASS 38/38 in
  0.09 s at 23,608 KB peak RSS.
- Scoped mutation suite: PASS 35/35 in 0.119 s (0.22 s enclosing wall time)
  at 24,760 KB peak RSS, including 34 adversarial mutations.
- Papers V and VI: PASS after two `pdflatex -halt-on-error` passes each.  The
  final passes took 0.51 s at 50,604 KB and 0.50 s at 51,176 KB peak RSS.
  The PDFs have 69 pages (696,357 bytes) and 61 pages (666,237 bytes), with
  SHA-256 hashes
  `c043cf2b1287470ad0da00b1abd21c914f02757cf480e105e395b410a5420f7f`
  and
  `5aaed69d9139ec7245d60ca85ee65e0a63eae9356f6dee153849684ec442878c`.
  No overfull box occurs at either inserted finite-bandwidth theorem; the
  logs retain only the papers' previously recorded boxes.
- Tier 3: FAIL-CLOSED, 2,672 tests in 697.125 s (698.13 s enclosing wall
  time) at 391,504 KB peak RSS, with 31 failures and 9 skips.  Every one of
  the 34 tests present in that run passed.  Relative to the preceding
  2,638-test run, the test count increases by exactly 34, all 31 present
  failure names are unchanged,
  and the old `chain_imports.test_c1_the_scan_actually_ran` failure is absent
  because that scan completed.  The two substantive chain-import findings
  and the other older content-addressed failures remain.  This is not a
  repository-wide pass and supports no freeze.
- The Science Forge planning fold accepted 1,545 nodes with zero invalid
  items and zero malformed events in 6.01 s at 263,248 KB peak RSS.  It ran
  outside the virtual-address cap because the Go runtime reserves a larger
  virtual page arena before execution.
- The advisory Science Forge shadow script exited zero by design in 1.99 s
  at 339,800 KB peak RSS, but its bridge audit is a fail-closed finding: the
  available Forge 0.0.2 binary has a standard-library hash mismatch and
  rejects the current prelude with `E9118`.  The coverage census reports
  1,612 certificates against the old 976-certificate baseline.  Neither
  finding is evidence for this theorem.

Tier 3 was required because Papers V and VI acquire a finite-bandwidth
coefficient theorem.  Tier 2 is the content-addressed four-predecessor chain
rechecked by the producer and independent verifier.  No classical input,
shared operator, quantum schema or quantum lifecycle state changed, so
unrelated classical and quantum freeze chains were not rebuilt separately.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_finite_bandwidth_dark_port_q8.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_finite_bandwidth_dark_port_q8.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_finite_bandwidth_dark_port_q8
```
