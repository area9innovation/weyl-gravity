# BT logarithmic-bubble homogeneous-virial no-go

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_VIRIAL_NO_GO_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

No nonnegative constant can make the homogeneous pointwise estimate

\[
                        D_L(\psi)\geq c A_L(\psi)
\]

valid on every four-dimensional periodic BT lattice.  This includes the last
open range \(0<c<1\), and even the sign claim \(D_L\geq0\).

The witness is one fixed smooth radial field on the unit flat four-torus.  Put
\(r_-=e^{-8}/8\), \(s=\log(r/r_-)\), and use the quintic smoothstep

\[
 W(z)=10z^3-15z^4+6z^5.
\]

The window rises as \(W(s/2)\) for two logarithmic units, stays at one for
four units, falls symmetrically for two units, and vanishes elsewhere.  Define

\[
                 \psi'(r)=-\frac{3}{2}\frac{w(s)}r.
\]

It is constant inside the inner ball and outside the annulus.  The matching of
\(W,W',W''\) makes \(\psi\) a \(C^3\) torus field.  Subtracting its mean changes
no edge difference.

## Exact continuum sign

Write \(X=\Delta\psi\) and \(Y=|\nabla\psi|^2\).  Removing only the positive
area factor \(|S^3|=2\pi^2\), exact rational polynomial integration gives

\[
 Q=\int X^2=\frac{1173}{22},\qquad
 C=\int XY=-\frac{2781}{77},\qquad
 P=\int Y^2=\frac{886707}{33592}.
\]

The four smoothstep moments used here are independently reconstructible:

\[
 \int_0^1W^2=\frac{181}{462},\quad
 \int_0^1W^3=\frac{26}{77},\quad
 \int_0^1W^4=\frac{2549}{8398},\quad
 \int_0^1(W')^2=\frac{10}{7}.
\]

Consequently

\[
 \frac{A_{\rm cont}}{2\pi^2}
 =\frac{Q+2C+P}{2}=\frac{19349691}{5173168}>0,
\]

while

\[
 \frac{D_{\rm cont}}{2\pi^2}
 =Q+3C+2P=-\frac{2896611}{1293292}<0.
\]

No floating-point value decides either sign.

## Transfer to finite lattices

Sample this same centered field on \((\mathbb Z/L\mathbb Z)^4\) with
\(h=1/L\).  Pairing the plus and minus increments in every coordinate and
using the uniform Taylor--Peano remainder for a \(C^2\) function gives

\[
 h^{-2}r_L\longrightarrow\Delta\psi+|\nabla\psi|^2,
 \qquad
 h^{-2}t_L\longrightarrow\Delta\psi+2|\nabla\psi|^2
\]

uniformly.  Since the number of sites is \(L^4=h^{-4}\), the action and
virial sums are ordinary four-dimensional Riemann sums.  Therefore

\[
 A_L\longrightarrow A_{\rm cont}>0,
 \qquad D_L\longrightarrow D_{\rm cont}<0.
\]

There is thus an \(L_0\) such that this explicit sequence has \(D_L<0\) for
every finite integer \(L\geq L_0\).

## Meaning for the continuum programme

The tuned estimate \(\mathbb E[A_L]=O(g_L^2N)\) cannot be proved by any
homogeneous radial Ward inequality, even after weakening its constant toward
zero.  The certified affine virial theorem survives because its additive
volume defect is essential.

This is a pointwise-method no-go, not a probability theorem.  The bubble may
be extremely rare under the normalized Gibbs measure.  The live route is now
to compare bubble rarity with the entropy of its locations and scales, or to
estimate the whole zero-fiber score by a genuinely Gibbs-weighted block or
large-deviation argument.

## Claim boundary

This result does not prove divergence of the actual interacting action or
\(H^{-1}\) moment, and it constructs no continuum measure.  It establishes no
Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` result.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_log_bubble_virial_no_go.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_log_bubble_virial_no_go.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_log_bubble_virial_no_go
```

## Tier receipt

- Tier 0: Python compilation and certificate/schema/event JSON parsing passed.
  The generated-appendix freshness check passed.  The final two-pass Paper 21
  build and undefined-reference/overfull-box log scan passed in 1.48 seconds.
  Scoped `git diff --check` and exact staged-diff inspection passed immediately
  before commit.
- Tier 1: exact producer replay passed in 0.04 seconds; the independent
  sparse-polynomial verifier passed in 0.09 seconds; nine direct and mutation
  tests passed in 0.11 seconds.  The Paper 21 claim-map producer and verifier
  passed in 0.13 and 0.08 seconds, respectively.
- Tier 2 was not run because no shared operator, shared schema, generated
  mathematical input, or input used by another certificate chain changed.
  The three predecessor certificates are content-pinned imports.
- Tier 3 is not required because this is a scoped method obstruction, not a
  freeze, shared-core change, release, or quantum lifecycle promotion.
- The append-only programme fold imported 1628 nodes with zero invalid items
  and zero malformed events.  The advisory Science Forge shadow rail ran but
  did not certify: its bridge audit hit the pre-existing external Forge
  toolchain/library mismatch (`E9118`), and its corpus census reported baseline
  drift.  Those advisory findings do not promote or invalidate this result.
