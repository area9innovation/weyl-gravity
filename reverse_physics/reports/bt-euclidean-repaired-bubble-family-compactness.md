# BT repaired-bubble family compactness

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_REPAIRED_BUBBLE_FAMILY_COMPACTNESS_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The locally repaired periodic sphere-bubble family cannot collapse the BT
Euler-gradient quotient.  On the (2\pi)-periodic four-torus, define

\[
 F_4(x)=\sum_{\mu=1}^4\left[
 \frac83(1-\cos x_\mu)-\frac16(1-\cos2x_\mu)\right],
 \qquad
 \Omega_m=\frac1{m+F_4},quad m>0.
\]

If (R_m=\Delta\Omega_m/\Omega_m), (E_m) is the flat (L^2) Euler
gradient of (rac12\int R_m^2), and

\[
                       Q(m)=\frac{\|E_m\|_2^2}{\|R_m\|_2^2},
\]

then there exists a constant (c_{F_4}>0) such that

\[
                            Q(m)\geq c_{F_4}
                            \qquad(m>0).
\]

The proof is qualitative but exact.  It compactifies the parameter by
(t=m/(1+m)), proves positive finite limits at both endpoints, and rules out
an interior zero by the weighted-current energy identity.  No numerical
quadrature is needed.

This closes one concrete branch: neither the naive chord bubble nor its
minimal fourth-order local repair produces a normalized torus-gradient
collapse.  It does not prove a lower bound for arbitrary periodic fields.

## The shrinking-bubble endpoint

The predecessor certificate proves the local jet

\[
 F_4=|x|^2-\frac1{90}\sum_\mu x_\mu^6+O(|x|^8).
\]

Writing (h_m=m+F_4) and

\[
 q_m=R_m/\Omega_m^2=-h_m\Delta F_4+2|\nabla F_4|^2,
\]

gives near the puncture

\[
 q_0=O(|x|^6),\qquad R_0=O(|x|^2),\qquad E_0=O(1).
\]

The terms containing (m) can be split at (|x|\sim\sqrt m).  In the core,
rescaling (x=\sqrt m,y) makes their (E_m)-contribution bounded while the
core volume is (O(m^2)).  Outside the core,
(E_m-E_0=O(m|x|^{-2})), whose squared four-dimensional integral tends to
zero.  Hence

\[
                         E_m\longrightarrow E_0
                         \quad\hbox{strongly in }L^2.
\]

The residual has a different limit because its radial core concentrates:

\[
 \|R_m\|_2^2\longrightarrow
 \frac{32\pi^2}{3}+\|R_0\|_2^2.
\]

The first term is exactly the round-sphere bubble energy.  The cross term
vanishes, and the remainder converges strongly away from the puncture.

It remains to show that (E_0) is not zero.  At the puncture (q_0\to0).
At (x=(\pi,0,0,0)), exact trigonometry gives

\[
 F_4=\frac{16}{3},\qquad
 \Delta F_4=\frac83,\qquad
 |\nabla F_4|^2=0,qquad
 q_0=-\frac{128}{9}.
\]

If (E_0=\operatorname{div}(F_4^{-2}\nabla q_0)) vanished, multiplying by
(q_0) and integrating by parts on the punctured torus would give

\[
                    \int F_4^{-2}|\nabla q_0|^2=0.
\]

The boundary term vanishes because (q_0=O(r^6)) and
(F_4^{-2}\nabla q_0=O(r)).  Thus (q_0) would be constant, contradicting
the two exact values.  Therefore

\[
 Q(0):=\frac{\|E_0\|_2^2}
 {32\pi^2/3+\|R_0\|_2^2}>0.
\]

## No zero at finite parameter

For any smooth positive periodic field, put

\[
 q=R/\Omega^2,qquad
 E=\operatorname{div}(\Omega^2\nabla q).
\]

If (E=0), testing against (q) gives

\[
                 \int\Omega^2|\nabla q|^2=0,
\]

so (q=c).  Equivalently,

\[
                         \Delta\Omega=c\Omega^3.
\]

Integration over the torus forces (c=0), and a periodic harmonic function
is constant.  Every (Omega_m=(m+F_4)^{-1}) with finite (m>0) is
nonconstant.  Consequently (E_m\ne0) and (Q(m)>0) throughout the open
parameter interval.

## The weak-field endpoint

As (m\to\infty),

\[
 R_m=-\frac{\Delta F_4}{m}+O(m^{-2}),
 \qquad
 E_m=-\frac{\Delta^2F_4}{m}+O(m^{-2}).
\]

Exact Fourier orthogonality gives

\[
                         Q(\infty)=\frac{32}{17}>0.
\]

This value is independently reconstructed in the verifier from the first-
and second-harmonic coefficients.

## Compactness in the family parameter

For (m>0), all fields and integrands depend smoothly on (m), so (Q) is
continuous.  The endpoint analysis extends it continuously under

\[
                         t=\frac{m}{1+m}
\]

to the closed interval (0\leq t\leq1).  It is positive at both endpoints
and at every interior point.  The extreme-value theorem therefore supplies

\[
                     c_{F_4}=\min_{0\leq t\leq1}Q(t)>0.
\]

The certificate deliberately records this constant as
`EXISTS_NOT_COMPUTED`.  Its value is unnecessary for ruling out a collapsing
sequence inside this family, but an explicit interval enclosure would be
needed to use it quantitatively elsewhere.

## Consequence for the main barrier

The one-sphere-bubble hypothesis has now survived two increasingly faithful
tests and failed as a collapse mechanism:

1. the standard chord periodization develops a logarithmically divergent
   Euler norm;
2. the fourth-order repaired periodization removes that divergence but has a
   strictly positive uniform quotient over its entire parameter family.

This does not exclude multi-bubbles, bubble towers, long necks, or unrelated
transverse-current profiles.  A general deterministic theorem would require
a profile decomposition proving that these are the only losses of
compactness and then controlling their interactions.

For progress toward the actual interacting estimate, the more direct next
route is now the connection-corrected Witten Schur problem.  The earlier
Gauss--Newton certificate already identifies the exact configuration-space
connection and residual-embedding curvature terms that a corrected inverse
must absorb.

## Boundaries

This result supplies no numerical value for (c_{F_4}), no all-field gradient
bound, no exclusion of multi-bubble or nonspherical collapse, no
Witten/Poincare theorem, no interacting Gibbs (H^{-1}) estimate, no
tightness or continuum identification, no Born rule or Krein reconstruction,
and nothing `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_repaired_bubble_family_compactness.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_repaired_bubble_family_compactness.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_repaired_bubble_family_compactness
```

The measured producer, independent-verifier, and test runs took (0.03),
(0.09), and (0.10) seconds at peak RSS (20{,}416), (30{,}152), and
(30{,}628) KiB.  Planning conformance validated the new sequence-47 event
but refused after 6.88 seconds at 205,136 KiB on ten pre-existing
`forge-requests` lifecycle errors.  The Science Forge shadow rail was not
rerun because no registered shadow input changed and the preceding bounded
attempt failed to produce a disposition after unrelated indexing processes
aborted; it is not counted as a pass.
