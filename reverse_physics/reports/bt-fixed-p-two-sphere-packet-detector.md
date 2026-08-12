# BT invariant fixed-P two-sphere packet detector

Certificate:
`REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The finite local BT packet detector now has a leakage bound on the complete
invariant two-body angular shell at one fixed timelike total momentum.  The
previous `dc` integral remains an operationally declared reduced measure; it
is not the invariant phase measure on its equatorial orbit.

At fixed total momentum, the massless two-body shell is a two-sphere.  The
order-20 projective Fejer filter has invariant equatorial leakage below

\[
 {331\over500000}=0.000662.
\]

Every Laurent mode can be homogenized to the same degree, giving one
antipodally even degree-38 polynomial filter on the full sphere.  With a
compact latitude band, exact integration gives

\[
 \boxed{0<\eta_{S^2}<{83\over125000}<10^{-3}.}
\]

The complement is retained in the star Hamiltonian.  At a half pulse the
selected bright packet is therefore absorbed with efficiency greater than

\[
 {124917\over125000}=0.999336.
\]

This closes the full-solid-angle gate at fixed total momentum.  It does not
close energy or total-momentum thickness or the omitted parts of the local
quadratic Hamiltonian.

## The invariant two-body shell

The selected lab-frame total momentum is

\[
 {P\over\kappa}=(2,-6/5,0,0),\qquad
 {P^2\over\kappa^2}={64\over25}.
\]

Its centre-of-momentum mass is \(M=8\kappa/5\).  In that frame every ordered
future massless pair is

\[
 k_1^*={4\kappa\over5}(1,n),\qquad
 k_2^*={4\kappa\over5}(1,-n),\qquad n\in S^2.
\]

The boost back to the lab has

\[
 \beta_x=-{3\over5},\qquad \gamma={5\over4}.
\]

Writing

\[
 n=(x,\sqrt{1-x^2}\cos\varphi,
       \sqrt{1-x^2}\sin\varphi),
\]

the individual lab energies are

\[
 {k_1^0\over\kappa}=1-{3x\over5},\qquad
 {k_2^0\over\kappa}=1+{3x\over5}.
\]

Thus the previously used equal-energy family is exactly the equator \(x=0\),
not the complete fixed-\(P\) shell.  The invariant two-body phase-space
measure is a \(P^2\)-dependent common constant times

\[
 d\Omega=dx\,d\varphi.
\]

On the equator its angular factor is \(d\varphi\), not \(dc\) for
\(c=\cos\varphi\).  The unordered pair quotient \(n\sim-n\) halves all the
norms below and cancels from every leakage ratio.

## Invariant equatorial calculation

Retain the projective coordinate

\[
 \zeta=e^{2i\varphi}
\]

and the order-20 filter

\[
 p(\varphi)={K_{20,0}(\varphi)-K_{20,1}(\varphi)\over1-\rho},
\]

with target lines (c=0,3/5).  It obeys

\[
 p(\pi/2)=1,\qquad
 p(\arccos(3/5))=-1
\]

exactly.  On \(0\leq\varphi<\pi\), choose

\[
 B_1^\varphi=[\pi/4,3\pi/8],\qquad
 B_0^\varphi=[3\pi/8,5\pi/8].
\]

They meet only at one measure-zero boundary and their \(L^2\) packet modes
are orthogonal.  Every endpoint is a root of unity.  Expanding

\[
 |p(\varphi)|^2=\sum_{m=-38}^{38}q_m e^{2im\varphi}
\]

makes every interval integral an exact element of

\[
 \mathbb Q\pi+\mathbb Q+\mathbb Q\sqrt2.
\]

Strict rational enclosures for \(\sqrt2\) follow from integer-square
comparisons.  Strict enclosures for \(\pi\) follow from the alternating
Machin identity

\[
 \pi=16\arctan(1/5)-4\arctan(1/239).
\]

The exact linear-form hashes and bounds give

\[
 \eta_\varphi
 =1-{\int_{B_0^\varphi\cup B_1^\varphi}|p|^2d\varphi
          \over\int_0^\pi|p|^2d\varphi}
 =0.000661284456502986486\ldots
 <{331\over500000}.
\]

No decimal establishes the inequality.

## One degree-38 local filter on the full sphere

The equatorial Laurent monomials by themselves are not polynomials at the
poles.  They admit a common homogeneous lift.  For \(m\geq0\),

\[
 (1-x^2)^{19}e^{2im\varphi}
 =(n_y^2+n_z^2)^{19-m}(n_y+in_z)^{2m},
\]

and for \(m<0\) use \(n_y-in_z\).  Every term has total degree

\[
 2(19-|m|)+2|m|=38.
\]

Consequently

\[
 \boxed{F(n)=(1-x^2)^{19}p(\varphi)}
\]

is a single degree-38 polynomial on the sphere.  Replacing (n_y,n_z) by
the normalized constant-coefficient transverse Fourier multipliers realizes
it as a local symmetrized quadratic density of derivative order 38.  Since
the degree is even,

\[
 F(-n)=F(n),
\]

so it descends to the unordered pair shell.  The full-sphere lift therefore
costs no derivative order beyond the equatorial filter.

## Latitude and combined leakage

Use the common compact latitude band

\[
 |x|\leq {1\over2}.
\]

The squared latitude weight is \((1-x^2)^{38}\).  Both its total norm and its
band norm are exact rational numbers:

\[
 I_{\rm tot}=\int_{-1}^{1}(1-x^2)^{38}dx,
 \qquad
 I_{\rm band}=\int_{-1/2}^{1/2}(1-x^2)^{38}dx.
\]

The resulting latitude leakage is

\[
 \eta_x=1-{I_{\rm band}\over I_{\rm tot}}
 =0.00000233295329801422291\ldots<3\times10^{-6}.
\]

Because the full norm factorizes,

\[
 1-\eta_{S^2}=(1-\eta_\varphi)(1-\eta_x).
\]

The exact algebraic interval comparison gives

\[
 \eta_{S^2}
 =0.000663615867055246985\ldots
 <{83\over125000}<10^{-3}.
\]

The two full-sphere packet regions are

\[
 B_j=\{|x|\leq1/2,\ \varphi\in B_j^\varphi\}.
\]

Their normalized restrictions of \(F\) are orthogonal.  Their norms are not
equal, so the earlier equal-normalized two-mode relative-\(q_8\) coefficient
does not transfer to these packets.

## Residual-retaining apparatus

Let \(B\) be the norm-weighted bright combination of the two packet modes,
\(D\) their dark combination, and \(R\) the normalized restriction of \(F\)
to the complete sphere complement.  The coupled direction is

\[
 v=\sqrt{1-\eta_{S^2}}B+\sqrt{\eta_{S^2}}R.
\]

The complete fixed-\(P\) rotating-wave star Hamiltonian is

\[
 {H\over G}=|e,0\rangle\langle g,v|+|g,v\rangle\langle e,0|.
\]

It obeys \((H/G)^3=H/G\), giving

\[
 U_\tau=I+[\cos(G\tau)-1](H/G)^2-i\sin(G\tau)(H/G).
\]

Compressing only after this full exponential yields

\[
 E_{\rm absorb}=(1-\eta_{S^2})\sin^2(G\tau)P_B,
\]

\[
 E_{\rm pass}=P_D+
 [1-(1-\eta_{S^2})\sin^2(G\tau)]P_B.
\]

At a half pulse,

\[
 1-\eta_{S^2}>{124917\over125000}.
\]

For every normalized initial state in the detector/bright plane and every
time, the outside-packet population obeys

\[
 P_{\rm outside}^{\rm max}
 =4\eta_{S^2}(1-\eta_{S^2})<{1\over375}.
\]

The calculation never substitutes

\[
 e^{-i\Pi H\Pi\tau}
\]

for the compression of the full evolution.

## What has and has not crossed the physical barrier

Established:

- the invariant fixed-timelike-\(P\) massless two-body sphere;
- the identification of the previous equal-energy family as its equator;
- the correction from operational \(dc\) to invariant equatorial \(d\varphi\);
- an antipodally even degree-38 local polynomial filter on the entire sphere;
- two normalizable full-sphere packets and exact algebraic norm receipts;
- invariant full-sphere leakage below \(83/125000\); and
- exact residual-retaining apparatus evolution at fixed \(P\).

Not established:

- finite invariant-mass or total-momentum bandwidth;
- control of number-scattering, counter-rotating or other off-resonant terms;
- practicality or minimality of the degree-38 anisotropic apparatus;
- selection of the apparatus by the public closed BT Hamiltonian;
- either absolute order-\(\lambda^8\) probability coefficient;
- transfer of the equal-mode relative-\(q_8\) result to the unequal packets;
- forward endpoints or real--virtual/KLN completion;
- an all-time Moller, LSZ or \(S\) operator;
- the standard scalar projector or general Eq.\ (19);
- a positive full physical Hilbert/Fock theory;
- gravity, metric BV--BRST, restored QME or residual transfer;
- anything `LORENTZIAN-CAUSAL`; or
- literature priority.

This result crosses the angular part of the physical detector barrier at one
fixed total momentum.  The next barrier is radial in momentum space rather
than angular: give the packets finite \(P\) and invariant-mass thickness and
control every term in the same finite-duration local interaction.

## Independent rail

The producer uses closed triangular Fejer coefficients, Gaussian-rational
convolution, root-of-unity integration in
\(\mathbb Q\pi+\mathbb Q+\mathbb Q\sqrt2\), binomial latitude
antiderivatives, integer-square radical bounds and alternating Machin bounds.

The verifier does not import the producer.  It reconstructs each Fejer kernel
from the direct \(20\times20\) amplitude double sum, integrates the roots of
unity with an independent complex-
\(\mathbb Q(\sqrt2)\) implementation, obtains the latitude band by an
integration-by-parts recurrence, obtains the total latitude norm from a beta
closed form, and nests independently tighter radical and Machin intervals
inside the stored bounds.  It also reconstructs the Lorentz boost and mass
shell coefficientwise and verifies \(H^3=H\) and unitarity on a rational
four-state fixture.

## Verification receipt

All scientific processes run sequentially under `ulimit -v 500000`.

- Python parse/compile: PASS, 0.04 s, 16,192 KB peak RSS.
- Exact producer and byte-drift check: PASS 39/39, 0.12 s,
  16,852 KB peak RSS.
- Independent direct-double-sum, recurrence and exact star verifier: PASS
  63/63, 0.29 s, 25,196 KB peak RSS.
- Mutation suite: PASS 43/43, 3.50 s, 24,868 KB peak RSS.
- Papers V and VI: PASS after two `pdflatex -halt-on-error` passes each.
  Their final passes took 0.49 s at 50,640 KB and 0.50 s at 51,152 KB peak
  RSS.  The PDFs have 64 pages (679,572 bytes) and 58 pages (655,923 bytes),
  with SHA-256 hashes
  `771673592fe25465fe697cd591d3fe2743bbf7f781931cfbcc02534cf542d6aa`
  and
  `2a94eb755b21ccd209f0cc7bd6027630186131b63e091e5d1fe6848feffdda77`.
  There are no undefined citations or references.  The logged overfull boxes
  are outside the inserted theorem locations.
- Paper prose advisory: NON-CERTIFYING findings.  Both manuscripts remain
  above the advisory parenthetical and abstract-ledger budgets inherited by
  the long programme papers; emphasis, em-dash, sentence-length, novelty and
  vocabulary checks are within their advisory budgets.  These measurements
  are not scientific gates.
- Tier 3: FAIL-CLOSED, 2,450 tests in 794.225 s, with 32 failures and 9
  skips; the enclosing timed process took 13:15.30 and peaked at 391,308 KB.
  All 43 new fixed-P sphere tests passed.  The failure and skip totals are
  unchanged from the predecessor 2,405-test run: older content-addressed
  producer/verifier rails and the capped chain-import scan remain failing,
  and the scan records that it did not run.  They are not passes.
- Science Forge advisory shadow rail: internally FAIL-CLOSED, advisory exit
  0 in 3.91 s at 60,024 KB.  The external caller helpers aborted under the
  cap and the Go bridge audit could not reserve page-summary memory, so its
  bridge audit failed with exit 2.  The independent coverage census reported
  1,607 certificates against the 976-certificate 2026-07-19 baseline.  No
  bridge-audit pass is claimed.

Exact scoped commands:

```bash
ulimit -v 500000
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fixed_p_two_sphere_packet_detector.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fixed_p_two_sphere_packet_detector.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fixed_p_two_sphere_packet_detector
```

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1.json`
