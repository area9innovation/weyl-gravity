# BT two-angle Fejér packet detector with residual-retaining evolution

Certificate:
`REVERSE_PHYSICS_BT_TWO_ANGLE_FEJER_PACKET_DETECTOR_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The exact zero-width locality obstruction can be bypassed quantitatively,
not exactly.  On the certified one-dimensional fixed-energy BT pair family,
an explicit finite-derivative local angular filter places more than
$99.9\%$ of its continuum coupling in two disjoint finite angular packets.

The complement is not discarded.  It is retained as an exact residual mode
in the Hamiltonian and exponentiated together with the two packet modes.  The
resulting selected packet instrument has absorption efficiency greater than
$999/1000$ at a half pulse.

This is the first local-detector successor which crosses the preceding
zero-width barrier without assuming that the selected packet sector is
invariant.

## Projective angle and the finite local filter

Write the continuous outgoing pair momenta as

\[
 k_1/\kappa=(1,-3/5,4c/5,4\sqrt{1-c^2}/5),\qquad
 k_2/\kappa=(1,-3/5,-4c/5,-4\sqrt{1-c^2}/5),
\]

where $c=\cos\theta$ and $0<\theta<\pi$.  The unordered pair is naturally
projective, so introduce

\[
 \zeta=e^{2i\theta}.
\]

The two target pair lines are

\[
 c_0=0,\qquad \zeta_0=-1,
\]

and

\[
 c_1={3\over5},\qquad
 \zeta_1={-7+24i\over25}.
\]

For order $N$, define the normalized projective Fejér kernel

\[
 K_{N,j}(\theta)=
 {1\over N^2}
 \left|\sum_{k=0}^{N-1}e^{2ik(\theta-\theta_j)}\right|^2.
\]

It is nonnegative, has $K_{N,j}(\theta_j)=1$, and is a finite Laurent
polynomial in $\zeta$ with modes $-(N-1),\ldots,N-1$.  At $N=20$, the
exact cross overlap is

\[
 \rho=K_{20,0}(\theta_1)
 ={5646762438667986757780624
 \over9094947017729282379150390625}
 <{1\over1000}.
\]

Therefore

\[
 p(\theta)={K_{20,0}(\theta)-K_{20,1}(\theta)\over1-\rho}
\]

obeys the exact interpolation conditions

\[
 p(\theta_0)=1,\qquad p(\theta_1)=-1.
\]

This is not merely an abstract angular function.  Let
$\mathcal D_+$ be the local transverse first-order operator whose Fourier
symbol on this fixed-energy shell is
$5(k_y+ik_z)/(4\kappa)$.  The pair symbol of

\[
 {1\over2}:\!\phi\mathcal D_+^{\,2m}\phi\!:
\]

is $e^{2im\theta}$.  Combining each mode with its conjugate realizes the
real Hermitian Laurent polynomial $p$ by a constant-coefficient local
quadratic density.  Its highest derivative order is

\[
 2(N-1)=38.
\]

The density is anisotropic apparatus structure.  It is local and finite
order, but it is not a Lorentz scalar by itself and it is not selected by the
public closed BT Hamiltonian.

## Two rational finite packets

Use the azimuthally reduced fixed-energy two-body measure $dc$ and the two
disjoint compact bins

\[
 B_0=\left[-{7\over25},{7\over25}\right],\qquad
 B_1=\left[{5\over13},{20\over29}\right].
\]

Both targets lie strictly inside their respective bins.  Every endpoint is
Pythagorean:

\[
 (7/25)^2+(24/25)^2=1,
\]

\[
 (5/13)^2+(12/13)^2=1,\qquad
 (20/29)^2+(21/29)^2=1.
\]

This makes the complete Fourier integrals exact rational numbers.  Define

\[
 T=\int_{-1}^{1}|p(c)|^2dc,\quad
 C_j=\int_{B_j}|p(c)|^2dc,\quad
 L=T-C_0-C_1,\quad
 \eta={L\over T}.
\]

The exact values are retained in canonical-fraction hashes and strict
rational enclosures.  Their readable values are

\[
 T\simeq0.186865823150923426,
\]

\[
 C_0\simeq0.103806266704272379,\qquad
 C_1\simeq0.0829174931988846096,
\]

\[
 L\simeq0.000142063247766437373,\qquad
 \boxed{\eta\simeq0.000760242003438472779<{1\over1000}.}
\]

No decimal establishes the inequality: the producer and verifier compare
the exact rational fraction directly with $1/1000$.

Define normalized packet modes

\[
 f_j={\mathbf1_{B_j}p\over\|\mathbf1_{B_j}p\|},
 \qquad g_j^2=C_j.
\]

Their supports are disjoint, so they are exactly orthonormal.  The selected
bright and dark combinations are

\[
 B={g_0f_0+g_1f_1\over\sqrt{g_0^2+g_1^2}},\qquad
 D={g_1f_0-g_0f_1\over\sqrt{g_0^2+g_1^2}}.
\]

Let $R$ be the normalized restriction of $p$ to the complement of the
two bins.  The complete normalized continuum direction coupled by the local
density is then

\[
 \boxed{v=\sqrt{1-\eta}\,B+\sqrt\eta\,R.}
\]

The prior exact-locality obstruction appears here as the strict fact
$\eta>0$.  The new result is that this unavoidable number is explicitly
smaller than $10^{-3}$.

## Exponentiating the residual instead of deleting it

In the resonant pair-annihilation/creation rotating-wave sector, let
$|e,0\rangle$ denote the excited detector with field vacuum.  The complete
star Hamiltonian is

\[
 {H\over G}=|e,0\rangle\langle g,v|
             +|g,v\rangle\langle e,0|.
\]

The dark packet $D$ is exactly uncoupled.  Since $(H/G)^3=H/G$, the full
exponential, including $R$, is

\[
 U_\tau=I+[\cos(G\tau)-1](H/G)^2-i\sin(G\tau)(H/G).
\]

For an incoming state in the selected packet plane, detector absorption has
the exact effect

\[
 \boxed{E_{\rm absorb}
 =(1-\eta)\sin^2(G\tau)P_B.}
\]

and

\[
 E_{\rm pass}=P_D+
 [1-(1-\eta)\sin^2(G\tau)]P_B.
\]

At the half pulse $G\tau=\pi/2$, the bright packet is absorbed with
probability

\[
 1-\eta>{999\over1000}.
\]

The total field remainder is exactly $\eta<1/1000$.  The population in the
outside-packet direction from an incoming $B$ is

\[
 \eta(1-\eta)[1-\cos(G\tau)]^2.
\]

More generally, maximizing over every normalized initial state in
$\operatorname{span}\{|e,0\rangle,|g,B\rangle\}$ and every time gives

\[
 P_{\rm outside}^{\rm max}=4\eta(1-\eta)<{1\over250}.
\]

Most importantly, the selected dynamics was obtained by compressing this
full residual-retaining exponential.  The calculation does not replace it by

\[
 e^{-i\Pi H\Pi\tau},
\]

which was the invalid step identified by the predecessor no-go theorem.

## What has become physical

Within the declared fixed-energy rotating-wave scalar sector, we now have:

- a finite-order local microscopic density rather than a nonlocal two-mode
  projector;
- two finite, normalizable angular packet modes rather than delta angles;
- an exact rational continuum leakage coefficient;
- the full residual mode retained in the Hamiltonian exponential;
- a normalized two-outcome selected packet instrument; and
- a half-pulse efficiency above $99.9\%$.

This is a controlled approximate local measurement, not a new fundamental
dimension and not a proof of the complete BT theory.

## Boundaries

The result does not establish:

- exact support on two zero-width continuum angles;
- a leakage bound on the full outgoing two-sphere;
- control of other energies, shapes or total momenta;
- control of the number-scattering and counter-rotating pieces of the complete
  local quadratic field Hamiltonian;
- practicality or minimality of a 38-derivative detector density;
- selection of the filter, bins, coupling or pulse by public BT dynamics;
- transfer of the earlier equal-weight two-mode effect or its relative
  order-$\lambda^8$ coefficient to these unequal-norm packet modes;
- either absolute order-$\lambda^8$ probability coefficient;
- either forward endpoint or a real--virtual/KLN completion;
- an all-time BT Møller, LSZ or $S$ operator;
- the standard scalar projector or general BT Eq. (19);
- gravity, metric BV--BRST, QME restoration or residual transfer;
- anything `LORENTZIAN-CAUSAL`; or
- literature priority.

The next detector gate is to thicken the packet in energy and azimuth and to
bound the off-resonant, number-scattering and counter-rotating sectors.  The
engineering gate is to optimize derivative order against leakage.  The
independent probability gate remains the absolute $q_8$ Gram and
$X_2$--$X_6$ interference.

## Independent rail

The producer expands the closed triangular Fourier coefficients of the Fejér
kernels and performs exact Gaussian-rational convolution.  The verifier does
not import it: it reconstructs each kernel from the direct $20\times20$
amplitude double sum, rebuilds the filter and $|p|^2$, and independently
evaluates the exact endpoint antiderivative of
$\sin\theta e^{2im\theta}$.  It recomputes every canonical fraction hash,
rational enclosure, target value and evolution bound.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000`.

- Python parse/compile: PASS, 0.02 s, 15,036 KB peak RSS.
- Exact producer and byte-drift check: PASS 32/32, 0.11 s,
  16,640 KB peak RSS.
- Independent direct-double-sum and exact star-matrix verifier: PASS 42/42,
  0.21 s, 24,384 KB peak RSS.
- Mutation suite: PASS 33/33, 2.79 s, 24,692 KB peak RSS.  Its first run
  correctly exposed that the verifier did not reject an absolute-$q_8$
  lifecycle promotion; that check was added before the final passing run.
- Papers V and VI: PASS after two `pdflatex -halt-on-error` passes each.
  The final passes took 0.50 s at 50,812 KB and 0.51 s at 51,180 KB peak
  RSS.  The PDFs have 64 pages (678,306 bytes) and 58 pages (654,848 bytes),
  respectively.  Their SHA-256 hashes are
  `28357e2e12bd5c8ff27f5756ded2a37b42b788b7a8f8e74ee2a96cb0ca68432e`
  and
  `1af9462b02844b3dea6d0b1faf7acfa165e9d822fb76588863108065f9b858b7`.
  There are no undefined citations or references; logged overfull boxes and
  `amsmath` warnings predate the inserted text.
- Tier 3: FAIL-CLOSED, 2,405 tests in 790.856 s, with 32 failures and 9
  skips; the enclosing timed process took 791.88 s and peaked at 391,628 KB.
  All 31 Fejér packet tests present during Tier 3 passed.  A subsequent
  claim-boundary and receipt tightening added two scoped mutations which also
  pass; they forbid transferring the unequal-norm packet result to the earlier
  equal-weight relative-$q_8$ formula and check the displayed decimal against
  the exact fraction.  Tier 3 was not repeated because those post-run changes
  narrow or independently check the claim and touch no mathematical input or
  shared operator.  The failure and skip totals are
  unchanged from the predecessor 2,374-test run: older content-addressed
  producer/verifier rails plus the capped chain-import scan remain failing,
  and the scan explicitly records that it did not run.  They are not passes.
- Science Forge advisory shadow rail: timeout/fail-closed, exit 124 at
  30.00 s and 59,976 KB peak RSS.  Its external `cbp` caller and location
  helpers aborted and the rail did not reach a bridge-audit or coverage
  summary.  No Science Forge result is claimed from this invocation.

Exact commands:

```bash
ulimit -v 500000
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_two_angle_fejer_packet_detector.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_two_angle_fejer_packet_detector.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_fejer_packet_detector
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest discover -v
timeout 30s ci/science-forge-shadow.sh
```

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_FEJER_PACKET_DETECTOR_V1.json`
