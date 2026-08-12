# BT two-angle local detector compression and continuum leakage obstruction

Certificate:
`REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `CLASSIFIED`.

## Result

The finite two-angle pointer effect has an exact microscopic local vertex on
the two selected Bateman--Turok pair modes.  It does **not** define an exact
two-angle local detector on the full continuum.  Finite-derivative locality
forces coupling to additional angles.

This separates two statements which must not be conflated:

1. the compression of a local quadratic detector vertex to the selected
   three-state carrier is the required pair-absorption Hamiltonian; and
2. that carrier is not invariant under the full local vertex, so exponentiating
   the compression does not give the compression of the full evolution.

## Exact local contrast on the rational modes

Import the two exact outgoing pairs at hard-angle parameters
$c=0$ and $c=3/5$.  In coordinates $(t,x,y,z)$, with momenta measured
in units of $\kappa$, both pairs have total four-momentum

\[
 P=k_1+k_2=(2,-6/5,0,0).
\]

After absorbing the common finite-box normalization into the effective
coupling, the normal-ordered density

\[
 D_+=:\!\phi^2\!:
\]

has vacuum-to-pair weights $(1,1)$.  The normalized derivative weights of
$:\!(\partial_y\phi)^2\!:$ are

\[
 -{k_{1y}k_{2y}\over\kappa^2}
   =\left(0,{144\over625}\right).
\]

Consequently

\[
 D_-=:\!\phi^2\!:
 -{625\over72\kappa^2}:\!(\partial_y\phi)^2\!:
\]

has the exact contrast weights

\[
 (1,-1).
\]

The same compact smearing Fourier coefficient multiplies both matrix elements
because the total momentum $P$ is the same.

## Arbitrary phase from a Hermitian detector

For the target pair-annihilation weights

\[
 {1\over\sqrt2}(1,-e^{-i\varphi}),
\]

set

\[
 \alpha={1-e^{-i\varphi}\over2\sqrt2},\qquad
 \beta ={1+e^{-i\varphi}\over2\sqrt2}.
\]

Then $L_\varphi=\alpha D_++\beta D_-$ has exactly those two weights.  A
non-Hermitian Hamiltonian is unnecessary.  If $|g\rangle,|e\rangle$ are
the detector states, then
$\langle e|\sigma_x|g\rangle=1$ and
$\langle e|\sigma_y|g\rangle=i$, so the Hermitian interaction

\[
 H_{\rm loc}=\sigma_x\otimes
 [\mathop{\rm Re}\alpha D_++\mathop{\rm Re}\beta D_-]
 +\sigma_y\otimes
 [\mathop{\rm Im}\alpha D_++\mathop{\rm Im}\beta D_-]
\]

has transition density $L_\varphi$.

The construction assumes a detector gap resonant with the common pair energy
and independently driven real detector quadratures.  The anisotropic
$y$-derivative is an apparatus orientation, not a Lorentz-invariant scalar
interaction by itself.

## Exact selected-sector compression

In the basis

\[
 |g,+_\varphi\rangle,\quad |g,-_\varphi\rangle,\quad
 |e,0_{\rm field}\rangle,
\]

the normalized compression is

\[
 {H_{\rm comp}\over G}=
 \begin{pmatrix}
 0&0&0\\
 0&0&1\\
 0&1&0
 \end{pmatrix}.
\]

The symmetric pair is dark and the antisymmetric pair undergoes exact Rabi
absorption into the detector.  With $\theta=G\tau$, the field Kraus maps are

\[
 K_{\rm pass}=P_+(\varphi)+\cos\theta P_-(\varphi),
 \qquad
 K_{\rm absorb}=-i\sin\theta
 |0_{\rm field}\rangle\langle-_\varphi|,
\]

and hence

\[
 E_{\rm pass}=P_+(\varphi)+\cos^2\theta P_-(\varphi),
 \qquad
 E_{\rm absorb}=\sin^2\theta P_-(\varphi).
\]

These effects coincide with the finite pointer apparatus.  The instruments
differ after the outcome: here absorption leaves the field vacuum, whereas
the finite pointer construction retained the angle mode.

## Why exact continuum selectivity is impossible

The certified BT family contains a continuous hard-angle parameter
$-1<c<1$ at fixed total momentum.  Compact spacetime smearing supplies the
common factor $\widetilde F(P)$, so it cannot distinguish angles within this
family.

Parameterize an interior fixed-energy angular orbit by
$z=e^{i\theta}$.  Restricting any local quadratic density with finitely many
derivatives to the orbit gives a finite Laurent polynomial

\[
 p(z)=\sum_{n=-d}^{d}a_nz^n.
\]

Exact support on only two zero-width angles would make $p$ vanish on the
open complement of those points.  But $q(z)=z^dp(z)$ is an ordinary
polynomial of degree at most $2d$.  Vanishing at infinitely many points on
that open complement forces $q\equiv0$, hence $p\equiv0$, contradicting
the required nonzero weights at the selected angles.

The general root argument is accompanied by exact finite Vandermonde
witnesses for Laurent degrees $0$ through $6$; all seven matrices have
full rank.  Those finite witnesses test the implementation but are not
substituted for the general polynomial theorem.

Therefore a nonzero finite-derivative local quadratic detector cannot have
exact support on only the two selected continuum angles.

## The exponential boundary

The matrix $H_{\rm comp}=\Pi H_{\rm loc}\Pi$ and its exponential are exact
on the selected carrier.  The no-go theorem shows that the full local
Hamiltonian generically maps this carrier into additional angular modes.
Thus the calculation does not establish

\[
 \Pi e^{-iH_{\rm loc}\tau}\Pi
   =e^{-i\Pi H_{\rm loc}\Pi\tau}.
\]

Calling the right-hand side the exact full microscopic detector would erase
the leakage and is forbidden by the certificate.

## Physical meaning and next gate

Established:

- exact local vacuum-to-pair matrix elements on the two rational modes;
- arbitrary relative phase from two real Hermitian detector quadratures;
- the exact selected three-state pair-absorption compression;
- equality of its two effects with the finite apparatus effects; and
- a no-go theorem for nonzero finite-derivative local densities with exact
  two-point angular support in the continuum.

Not established:

- invariance of the selected sector under the full local Hamiltonian;
- equality of compressed full evolution with evolution of the compression;
- a leakage bound for finite angular bins or wavepackets;
- either absolute order-$\lambda^8$ probability coefficient;
- a real--virtual, survival, collinear or KLN completion;
- general Bateman--Turok Eq. (19), an all-time scattering operator, or
  selection by the public closed BT dynamics;
- gravity, metric BV--BRST, QME restoration, residual transfer, or anything
  `LORENTZIAN-CAUSAL`; or
- literature priority.

The nearest physical repair is to replace the two zero-width modes by two
disjoint compact angular wavepackets and compute the full leakage matrix of
$D_+$ and $D_-$.  A quantitative small-leakage bound would turn the exact
compression into an approximate local detector with a declared error.
Exact selection instead requires nonlocal or infinite-derivative structure,
or an enlarged instrument which records the continuum leakage.

## Independent rail

The producer uses exact SymPy rational and algebraic arithmetic for the pair
matrix elements, phase synthesis, selected compression and Vandermonde
witnesses.  The verifier does not import the producer.  It reconstructs the
momenta and density weights with `Fraction` arithmetic, checks phase
synthesis on four exact complex phases, recomputes the compression and
effects, and establishes the finite Vandermonde ranks by independent exact
Gaussian elimination.  Mutation tests require it to reject altered matrix
elements, phases, matrices, no-go facts, provenance and claim promotions.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000`.

- Python parse/compile: PASS, 0.04 s, 15,140 KB peak RSS.
- An invocation without the required producer mode: correctly rejected with
  exit status 2, 1.98 s, 79,268 KB peak RSS; it is not counted as a pass.
- Exact producer in `--check` mode: PASS 27/27, 1.92 s,
  79,140 KB peak RSS.
- Independent verifier: PASS 29/29, 0.09 s, 24,236 KB peak RSS.
- Mutation suite: PASS 26/26, 0.39 s, 24,816 KB peak RSS.
- Papers V and VI: PASS after two `pdflatex -halt-on-error` passes each.
  Their final passes took 0.50 s at 50,460 KB and 0.50 s at 50,780 KB peak
  RSS.  The PDFs have 63 pages (674,031 bytes) and 57 pages (652,514 bytes),
  respectively.  Their SHA-256 hashes are
  `f788fdabb4748d8ef9041e82c6b1f86ad1e03904dff20b4976daa48d5f04621a`
  and
  `89a35ac500b0a058a288bfcfd17591cbb114a0651bcc888c53469b3ba89aceab`.
  There are no undefined citations or references.  The logged
  overfull boxes and `amsmath` foreign-command warnings predate the inserted
  text.  An initial build attempt exposed invalid inline-math delimiters in
  the new prose; both PDFs were withheld by `-halt-on-error`, the source was
  repaired, and only the subsequent successful two-pass builds are retained.
- Tier 3: FAIL-CLOSED, 2,374 tests in 789.071 s, with 32 failures and 9
  skips; the enclosing timed process took 790.09 s and peaked at 391,580 KB.
  All 26 new locality tests passed.  The failure/skip totals are unchanged
  from the predecessor 2,348-test apparatus run: older content-addressed
  producer/verifier rails and the capped chain-import scan remain failing,
  and the scan explicitly records that it did not run.  They are not passes.
- Science Forge advisory shadow rail: FAIL-CLOSED internally, advisory exit
  0 in 3.91 s at 59,684 KB peak RSS.  Under the cap its Go bridge audit could
  not reserve runtime page-summary memory and reported `FAIL` with exit 2;
  the independent coverage census completed and reported 1,605 certificates
  against the 976-certificate 2026-07-19 baseline.  No bridge-audit pass is
  claimed.

Exact commands:

```bash
ulimit -v 500000
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m py_compile reverse_physics/bt_two_angle_local_detector_compression.py reverse_physics/verify_bt_two_angle_local_detector_compression.py reverse_physics/tests/test_bt_two_angle_local_detector_compression.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_two_angle_local_detector_compression.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_two_angle_local_detector_compression.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_local_detector_compression
cd paper && pdflatex -interaction=nonstopmode -halt-on-error 05-interaction-obstructions.tex
cd paper && pdflatex -interaction=nonstopmode -halt-on-error 06-einstein-weyl-interaction-obstructions.tex
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest discover -v
ci/science-forge-shadow.sh
```

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1.json`
